from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import boto3
import botocore
from botocore.exceptions import ClientError
import os
from datetime import datetime
import tempfile
import zipfile
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION"]
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/s3/buckets', methods=['GET'])
def list_buckets():
    """List all available S3 buckets"""
    try:
        response = s3_client.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return jsonify({"buckets": buckets})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/s3/directories', methods=['GET'])
def list_directories():
    """List directories in a specific S3 bucket"""
    bucket_name = request.args.get('bucket')
    if not bucket_name:
        return jsonify({"error": "bucket parameter is required"}), 400

    try:
        # List objects in the bucket
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Delimiter='/'
        )

        # Extract directory names (common prefixes)
        directories = []
        if 'CommonPrefixes' in response:
            directories = [prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']]

        # Get directory metadata including last modified dates
        dir_info = []
        for directory in directories:
            # Get the most recent object in each directory
            dir_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=directory + '/',
                MaxKeys=1000  # Limit to avoid timeouts
            )

            if 'Contents' in dir_response:
                # Get the most recent modification date
                last_modified = max(obj['LastModified'] for obj in dir_response['Contents'])
                image_count = sum(1 for obj in dir_response['Contents']
                                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')))

                dir_info.append({
                    "name": directory,
                    "last_modified": last_modified.isoformat(),
                    "image_count": image_count
                })

        # Sort by last modified date (newest first)
        dir_info.sort(key=lambda x: x['last_modified'], reverse=True)

        return jsonify({"directories": dir_info})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/s3/latest-directory', methods=['GET'])
def get_latest_directory():
    """Get the latest directory and its image keys"""
    bucket_name = request.args.get('bucket')
    if not bucket_name:
        return jsonify({"error": "bucket parameter is required"}), 400

    try:
        # Get all directories
        dirs_response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Delimiter='/'
        )

        if 'CommonPrefixes' not in dirs_response:
            return jsonify({"error": "No directories found"}), 404

        directories = [prefix['Prefix'].rstrip('/') for prefix in dirs_response['CommonPrefixes']]

        # Find the latest directory based on modification time
        latest_dir = None
        latest_time = None

        for directory in directories:
            dir_response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=directory + '/'
            )

            if 'Contents' in dir_response:
                max_time = max(obj['LastModified'] for obj in dir_response['Contents'])
                if latest_time is None or max_time > latest_time:
                    latest_time = max_time
                    latest_dir = directory

        if not latest_dir:
            return jsonify({"error": "No valid directories found"}), 404

        # Get all image keys from the latest directory
        images_response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=latest_dir + '/'
        )

        image_keys = []
        if 'Contents' in images_response:
            image_keys = [
                obj['Key'] for obj in images_response['Contents']
                if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))
            ]

        return jsonify({
            "directory": latest_dir,
            "last_modified": latest_time.isoformat(),
            "image_keys": image_keys,
            "image_count": len(image_keys)
        })
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/s3/download-directory', methods=['POST'])
def download_directory_images():
    """Download all images from a specific directory"""
    data = request.get_json()
    bucket_name = data.get('bucket')
    directory = data.get('directory')

    if not bucket_name or not directory:
        return jsonify({"error": "bucket and directory parameters are required"}), 400

    try:
        # List all images in the directory
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=directory + '/'
        )

        if 'Contents' not in response:
            return jsonify({"error": "No files found in directory"}), 404

        image_files = [
            obj for obj in response['Contents']
            if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))
        ]

        if not image_files:
            return jsonify({"error": "No image files found in directory"}), 404

        # Create a temporary directory to store downloaded images
        temp_dir = tempfile.mkdtemp()
        downloaded_files = []

        try:
            for img_obj in image_files:
                key = img_obj['Key']
                filename = os.path.basename(key)
                local_path = os.path.join(temp_dir, filename)

                # Download the file
                s3_client.download_file(bucket_name, key, local_path)
                downloaded_files.append({
                    "key": key,
                    "filename": filename,
                    "local_path": local_path,
                    "size": img_obj['Size']
                })

            return jsonify({
                "status": "success",
                "directory": directory,
                "downloaded_count": len(downloaded_files),
                "files": downloaded_files,
                "temp_directory": temp_dir
            })

        except Exception as download_error:
            # Clean up temp directory on error
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise download_error

    except ClientError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.post("/api/s3/image-keys")
def image_keys():
    """
    Body JSON:
    {
      "bucket": "<bucket-name>",
      "keys": ["prefix/a.jpg", "prefix/b.jpg", ...]
    }

    Response JSON (200):
    {
      "bucket": "<bucket-name>",
      "valid_count": <int>,
      "invalid_count": <int>,
      "valid_keys": [...],
      "invalid_keys": [{"key":"...", "reason":"File not found"}]
    }
    """
    # Parse JSON without raising 415 if Content-Type isn't application/json
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Invalid JSON payload: expected JSON with 'bucket' and 'keys'"), 400

    bucket = payload.get("bucket")
    keys = payload.get("keys")

    if not bucket or not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
        return jsonify(error="Missing or invalid 'bucket' or 'keys' (keys must be a list of strings)"), 400

    # Deduplicate while preserving order
    seen = set()
    deduped_keys = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            deduped_keys.append(k)

    # Verify bucket exists / is accessible
    try:
        s3_client.head_bucket(Bucket=bucket)
    except botocore.exceptions.ClientError as e:
        # Match your other tests that expect 500 on bad bucket
        return jsonify(error="S3 error checking bucket", detail=str(e)), 500

    valid_keys = []
    invalid_keys = []

    for key in deduped_keys:
        try:
            s3_client.head_object(Bucket=bucket, Key=key)
            valid_keys.append(key)
        except botocore.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("404", "NoSuchKey", "NotFound"):
                invalid_keys.append({"key": key, "reason": "File not found"})
            else:
                invalid_keys.append({"key": key, "reason": f"S3 error: {code or 'Unknown'}"})

    return jsonify(
        bucket=bucket,
        valid_count=len(valid_keys),
        invalid_count=len(invalid_keys),
        valid_keys=valid_keys,
        invalid_keys=invalid_keys
    ), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)