"""
Video Generation Service using Google's Veo API
Adapted for Flask backend integration
"""

import base64
import time
import requests
import os
import tempfile
import subprocess
from typing import List, Dict, Any, Optional
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import storage
import boto3
from botocore.exceptions import ClientError

class VideoGenerationService:
    def __init__(self, project_id: str, s3_client=None):
        self.project_id = project_id
        self.s3_client = s3_client
        self.base_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/veo-2.0-generate-exp"

    def get_access_token(self) -> str:
        """Get Google Cloud access token"""
        try:
            creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            creds.refresh(Request())
            return creds.token
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")

    def image_to_base64(self, file_path: str) -> str:
        """Convert image file to base64 string"""
        try:
            with open(file_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            raise Exception(f"Failed to encode image {file_path}: {str(e)}")

    def s3_image_to_base64(self, bucket: str, key: str) -> str:
        """Download S3 image and convert to base64"""
        if not self.s3_client:
            raise Exception("S3 client not initialized")

        try:
            # Download image to temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                self.s3_client.download_file(bucket, key, temp_file.name)
                return self.image_to_base64(temp_file.name)
        except ClientError as e:
            raise Exception(f"Failed to download S3 image {bucket}/{key}: {str(e)}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass

    def prepare_images_from_s3(self, bucket: str, image_keys: List[str]) -> List[Dict]:
        """Prepare image list from S3 keys"""
        image_list = []

        for key in image_keys:
            try:
                # Clean up the key - remove any s3:// prefix and bucket name if present
                clean_key = self.clean_s3_key(key, bucket)

                base64_image = self.s3_image_to_base64(bucket, clean_key)

                # Determine MIME type from file extension
                extension = clean_key.lower().split('.')[-1]
                mime_type = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'bmp': 'image/bmp'
                }.get(extension, 'image/jpeg')

                image_list.append({
                    "image": {
                        "bytesBase64Encoded": base64_image,
                        "mimeType": mime_type
                    },
                    "referenceType": "asset"
                })
                print(f"✅ Successfully processed image: {clean_key}")
            except Exception as e:
                print(f"Warning: Failed to process image {key}: {str(e)}")
                continue

        if not image_list:
            raise Exception("No valid images could be processed")

        return image_list

    def clean_s3_key(self, key: str, expected_bucket: str) -> str:
        """Clean S3 key to remove prefixes and ensure correct format"""
        # Remove s3:// prefix if present
        if key.startswith("s3://"):
            key = key[5:]

        # Remove bucket name prefix if present
        if key.startswith(f"{expected_bucket}/"):
            key = key[len(f"{expected_bucket}/"):]
        elif key.startswith("htn-test-bucket/"):
            key = key[len("htn-test-bucket/"):]
        elif key.startswith("htn-bucket-test/"):
            key = key[len("htn-bucket-test/"):]

        return key

    def start_video_generation(self, bucket: str, image_keys: List[str], prompt: str, duration: int = 8) -> str:
        """Start video generation process"""
        print(f"🎬 Starting video generation with {len(image_keys)} images")

        # Get access token with detailed error handling
        try:
            access_token = self.get_access_token()
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}. Please check your Google Cloud credentials and permissions.")

        # Prepare images with detailed logging
        try:
            image_list = self.prepare_images_from_s3(bucket, image_keys)
            print(f"✅ Prepared {len(image_list)} images for video generation")
        except Exception as e:
            raise Exception(f"Failed to prepare images from S3: {str(e)}")

        request_payload = {
            "instances": [{
                "prompt": prompt,
                "referenceImages": image_list
            }],
            "parameters": {
                "durationSeconds": duration,
                "storageUri": "gs://htn-bucket-test/",
                "sampleCount": 1
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        print(f"🚀 Calling Veo API with prompt: {prompt[:100]}...")

        try:
            response = requests.post(
                f"{self.base_url}:predictLongRunning",
                headers=headers,
                json=request_payload,
                timeout=60
            )
        except requests.exceptions.Timeout:
            raise Exception("Video generation request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during video generation request: {str(e)}")

        if response.status_code == 403:
            error_details = response.text
            raise Exception(f"Permission denied (403): Your Google Cloud account lacks permissions for Vertex AI Veo API. Error details: {error_details}")
        elif response.status_code == 404:
            raise Exception(f"Veo API not found (404): The Veo model may not be available in your region or project")
        elif not response.ok:
            error_msg = f"Video generation request failed with status {response.status_code}: {response.text}"
            raise Exception(error_msg)

        try:
            result = response.json()
            operation_name = result.get("name")
            if not operation_name:
                raise Exception("No operation name returned from Veo API")

            print(f"✅ Video generation started successfully: {operation_name}")
            return operation_name
        except ValueError as e:
            raise Exception(f"Invalid JSON response from Veo API: {str(e)}")

    def check_video_status(self, operation_name: str) -> Dict[str, Any]:
        """Check video generation status"""
        access_token = self.get_access_token()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        body = {"operationName": operation_name}

        response = requests.post(
            f"{self.base_url}:fetchPredictOperation",
            headers=headers,
            json=body
        )

        if not response.ok:
            raise Exception(f"Status check failed: {response.status_code} - {response.text}")

        return response.json()

    def wait_for_completion(self, operation_name: str, max_wait_time: int = 600) -> Dict[str, Any]:
        """Wait for video generation to complete"""
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            status = self.check_video_status(operation_name)

            if status.get("done"):
                videos = status.get("response", {}).get("videos", [])
                if videos:
                    return videos[0]
                raise Exception("Video generation completed but no video found in response")

            # Wait before next check
            time.sleep(10)

        raise Exception(f"Video generation timed out after {max_wait_time} seconds")

    def download_video_from_gcs(self, gcs_uri: str, destination_path: str) -> str:
        """Download video from Google Cloud Storage"""
        if not gcs_uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI format")

        try:
            # Parse GCS URI
            parts = gcs_uri[5:].split("/", 1)
            bucket_name = "htn-bucket-test"
            blob_name = parts[1]

            # Initialize GCS client
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Download video
            blob.download_to_filename(destination_path)
            return destination_path

        except Exception as e:
            raise Exception(f"Failed to download video from GCS: {str(e)}")

    def get_video_duration(self, video_path: str) -> float:
        """Get actual video duration using ffprobe"""
        try:
            # Use ffprobe to get video duration
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries',
                'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                video_path
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return round(duration, 2)
            else:
                print(f"Warning: Could not get video duration for {video_path}")
                return 8.0  # Default fallback
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, FileNotFoundError):
            print(f"Warning: ffprobe not available or failed, using default duration")
            return 8.0  # Default fallback
        except Exception as e:
            print(f"Warning: Error getting video duration: {e}")
            return 8.0  # Default fallback

    def generate_video_complete(self, bucket: str, image_keys: List[str], prompt: str, duration: int = 8) -> Dict[str, Any]:
        """Complete video generation workflow"""
        try:
            # Start generation
            operation_name = self.start_video_generation(bucket, image_keys, prompt, duration)

            # Wait for completion
            video_info = self.wait_for_completion(operation_name)

            # Create temporary file for video
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_video.close()

            # Download video
            gcs_uri = video_info.get("gcsUri")
            if gcs_uri:
                self.download_video_from_gcs(gcs_uri, temp_video.name)

            return {
                "success": True,
                "operation_name": operation_name,
                "video_info": video_info,
                "local_video_path": temp_video.name,
                "gcs_uri": gcs_uri
            }

        except Exception as e:
            print(e)
            return {
                "success": False,
                "error": str(e),
                "operation_name": operation_name if 'operation_name' in locals() else None
            }


# Utility functions for async video generation tracking
class VideoGenerationManager:
    def __init__(self):
        self.active_generations = {}  # operation_name -> generation_info

    def start_generation(self, project_id: str, operation_name: str, bucket: str, image_keys: List[str], prompt: str) -> str:
        """Track a new video generation"""
        generation_id = f"gen_{int(time.time())}_{len(self.active_generations)}"

        self.active_generations[generation_id] = {
            "operation_name": operation_name,
            "project_id": project_id,
            "bucket": bucket,
            "image_keys": image_keys,
            "prompt": prompt,
            "status": "generating",
            "started_at": time.time(),
            "progress": 0
        }

        return generation_id

    def update_status(self, generation_id: str, status: str, progress: int = None, video_info: Dict = None):
        """Update generation status"""
        if generation_id in self.active_generations:
            self.active_generations[generation_id]["status"] = status
            if progress is not None:
                self.active_generations[generation_id]["progress"] = progress
            if video_info:
                self.active_generations[generation_id]["video_info"] = video_info

    def get_status(self, generation_id: str) -> Optional[Dict]:
        """Get generation status"""
        return self.active_generations.get(generation_id)

    def remove_generation(self, generation_id: str):
        """Remove completed generation from tracking"""
        if generation_id in self.active_generations:
            del self.active_generations[generation_id]