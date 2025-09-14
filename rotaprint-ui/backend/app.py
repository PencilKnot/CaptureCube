from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import boto3
import botocore
from botocore.exceptions import ClientError
import os
import threading
import uuid
from datetime import datetime
import tempfile
import zipfile
from collections import defaultdict
from dotenv import load_dotenv
from services.video_generation import VideoGenerationService, VideoGenerationManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION"]
)

# Initialize video generation services
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "htn-scanner")
video_service = VideoGenerationService(PROJECT_ID, s3_client)
video_manager = VideoGenerationManager()

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


# Video Generation Endpoints

@app.route('/api/video/generate', methods=['POST'])
def start_video_generation():
    """Start video generation from S3 images"""
    data = request.get_json()

    bucket = data.get('bucket')
    image_keys = data.get('image_keys', [])
    prompt = data.get('prompt', "Cinematic close-up of a keychain charm with blue keycaps and white switches. Faithfully reproduce the shape, colors, and details from the reference image. Well-lit, ultra-high-resolution, sharp focus, minimal noise. Minimalist neutral background, soft shadows, realistic reflections. Product isolated in frame, camera slowly rotates around the charm to show all angles. Don't add any new features/characterstics to the product that are not in the reference image.")
    duration = data.get('duration', 8)

    if not bucket or not image_keys:
        return jsonify({"error": "bucket and image_keys are required"}), 400

    if not isinstance(image_keys, list) or len(image_keys) == 0:
        return jsonify({"error": "image_keys must be a non-empty list"}), 400

    try:
        # Generate unique generation ID
        generation_id = str(uuid.uuid4())

        # Start video generation in background thread
        def generate_video():
            try:
                print(f"🎬 Starting video generation for {generation_id}")

                # Update status to downloading (preparing images)
                video_manager.update_status(generation_id, "downloading", 10)

                # Test authentication first
                try:
                    access_token = video_service.get_access_token()
                    print(f"✅ Authentication successful")
                except Exception as auth_error:
                    raise Exception(f"Google Cloud authentication failed: {str(auth_error)}. Please check your service account credentials.")

                # Update status to processing images
                video_manager.update_status(generation_id, "processing", 20)

                # Start the video generation process
                operation_name = video_service.start_video_generation(
                    bucket, image_keys, prompt, duration
                )
                print(f"✅ Video generation started with operation: {operation_name}")

                # Track the generation
                video_manager.start_generation(
                    PROJECT_ID, operation_name, bucket, image_keys, prompt
                )
                video_manager.update_status(generation_id, "generating", 30)

                # Wait for completion with progress updates
                print(f"⏳ Waiting for video generation to complete...")
                video_info = video_service.wait_for_completion(operation_name)
                print(f"✅ Video generation completed")

                video_manager.update_status(generation_id, "downloading", 80)

                # Download video to temporary file
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                temp_video.close()

                gcs_uri = video_info.get("gcsUri")
                if gcs_uri:
                    print(f"📥 Downloading video from: {gcs_uri}")
                    video_service.download_video_from_gcs(gcs_uri, temp_video.name)
                    video_manager.update_status(generation_id, "completed", 100, {
                        "video_path": temp_video.name,
                        "gcs_uri": gcs_uri,
                        "video_info": video_info
                    })
                    print(f"✅ Video generation completed successfully")
                else:
                    raise Exception("No GCS URI returned from video generation")

            except Exception as e:
                error_msg = str(e)
                print(f"❌ Video generation failed: {error_msg}")
                video_manager.update_status(generation_id, "error", 0, {
                    "error": error_msg
                })

        # Start background thread
        thread = threading.Thread(target=generate_video)
        thread.daemon = True
        thread.start()

        # Initialize tracking
        video_manager.active_generations[generation_id] = {
            "status": "starting",
            "progress": 0,
            "bucket": bucket,
            "image_keys": image_keys,
            "prompt": prompt,
            "duration": duration,
            "started_at": datetime.now().isoformat()
        }

        return jsonify({
            "generation_id": generation_id,
            "status": "started",
            "message": "Video generation started successfully"
        }), 202

    except Exception as e:
        return jsonify({"error": f"Failed to start video generation: {str(e)}"}), 500

@app.route('/api/video/status/<generation_id>', methods=['GET'])
def get_video_generation_status(generation_id):
    """Get video generation status"""
    status_info = video_manager.get_status(generation_id)

    if not status_info:
        return jsonify({"error": "Generation ID not found"}), 404

    return jsonify({
        "generation_id": generation_id,
        "status": status_info.get("status", "unknown"),
        "progress": status_info.get("progress", 0),
        "bucket": status_info.get("bucket"),
        "image_count": len(status_info.get("image_keys", [])),
        "prompt": status_info.get("prompt"),
        "started_at": status_info.get("started_at"),
        "video_info": status_info.get("video_info")
    })

@app.route('/api/video/download/<generation_id>', methods=['GET'])
def download_generated_video(generation_id):
    """Download generated video file"""
    status_info = video_manager.get_status(generation_id)

    if not status_info:
        return jsonify({"error": "Generation ID not found"}), 404

    if status_info.get("status") != "completed":
        return jsonify({
            "error": "Video not ready for download",
            "status": status_info.get("status")
        }), 400

    video_info = status_info.get("video_info", {})
    video_path = video_info.get("video_path")

    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": "Video file not found"}), 404

    try:
        return send_file(
            video_path,
            as_attachment=True,
            download_name=f"advertisement_{generation_id}.mp4",
            mimetype='video/mp4'
        )
    except Exception as e:
        return jsonify({"error": f"Failed to send video file: {str(e)}"}), 500

@app.route('/api/video/generations', methods=['GET'])
def list_video_generations():
    """List all video generations"""
    generations = []

    for gen_id, info in video_manager.active_generations.items():
        generations.append({
            "generation_id": gen_id,
            "status": info.get("status"),
            "progress": info.get("progress", 0),
            "bucket": info.get("bucket"),
            "image_count": len(info.get("image_keys", [])),
            "prompt": info.get("prompt", "")[:100] + "..." if len(info.get("prompt", "")) > 100 else info.get("prompt", ""),
            "started_at": info.get("started_at")
        })

    # Sort by started_at (newest first)
    generations.sort(key=lambda x: x.get("started_at", ""), reverse=True)

    return jsonify({
        "generations": generations,
        "total_count": len(generations)
    })

@app.route('/api/video/cleanup/<generation_id>', methods=['DELETE'])
def cleanup_video_generation(generation_id):
    """Clean up completed video generation"""
    status_info = video_manager.get_status(generation_id)

    if not status_info:
        return jsonify({"error": "Generation ID not found"}), 404

    try:
        # Clean up video file if it exists
        video_info = status_info.get("video_info", {})
        video_path = video_info.get("video_path")

        if video_path and os.path.exists(video_path):
            os.unlink(video_path)

        # Remove from tracking
        video_manager.remove_generation(generation_id)

        return jsonify({"message": "Video generation cleaned up successfully"})

    except Exception as e:
        return jsonify({"error": f"Failed to cleanup: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)