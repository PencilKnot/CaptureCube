#!/usr/bin/env python3
"""
Test S3 key processing for video generation
"""

import requests
from services.video_generation import VideoGenerationService
import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ["AWS_REGION"]
)

def test_s3_key_cleaning():
    """Test S3 key cleaning functionality"""
    print("🧪 Testing S3 Key Cleaning")
    print("-" * 40)

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "htn-scanner")
    video_service = VideoGenerationService(project_id, s3_client)

    test_cases = [
        ("s3://htn-test-bucket/run_2025-09-14_04-21-42/0a.jpg", "run_2025-09-14_04-21-42/0a.jpg"),
        ("htn-test-bucket/run_2025-09-14_04-21-42/1a.jpg", "run_2025-09-14_04-21-42/1a.jpg"),
        ("run_2025-09-14_04-21-42/2a.jpg", "run_2025-09-14_04-21-42/2a.jpg"),
        ("htn-bucket-test/some/path/image.jpg", "some/path/image.jpg")
    ]

    for input_key, expected_output in test_cases:
        cleaned_key = video_service.clean_s3_key(input_key, "htn-test-bucket")
        status = "✅" if cleaned_key == expected_output else "❌"
        print(f"{status} '{input_key}' -> '{cleaned_key}' (expected: '{expected_output}')")

def test_get_latest_directory():
    """Test getting latest directory from S3"""
    print("\n🗂️  Testing Latest Directory Retrieval")
    print("-" * 40)

    try:
        response = requests.get("http://localhost:8000/api/s3/latest-directory?bucket=htn-test-bucket", timeout=30)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Latest directory: {data.get('directory')}")
            print(f"✅ Image count: {data.get('image_count')}")
            print(f"✅ Sample keys: {data.get('image_keys', [])[:3]}")
            return data.get('image_keys', [])[:3]
        else:
            print(f"❌ Failed to get latest directory: {response.status_code}")
            print(f"   Response: {response.text}")
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_s3_key_validation(image_keys):
    """Test S3 key validation"""
    print("\n🔍 Testing S3 Key Validation")
    print("-" * 40)

    if not image_keys:
        print("❌ No image keys to validate")
        return

    payload = {
        "bucket": "htn-test-bucket",
        "keys": image_keys
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/s3/image-keys",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Valid keys: {data.get('valid_count')}")
            print(f"✅ Invalid keys: {data.get('invalid_count')}")

            for valid_key in data.get('valid_keys', []):
                print(f"   ✅ {valid_key}")

            for invalid_item in data.get('invalid_keys', []):
                print(f"   ❌ {invalid_item.get('key')}: {invalid_item.get('reason')}")

        else:
            print(f"❌ Validation failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 S3 Key Processing Test Suite")
    print("=" * 50)

    # Test key cleaning
    test_s3_key_cleaning()

    # Test latest directory
    image_keys = test_get_latest_directory()

    # Test key validation
    test_s3_key_validation(image_keys)

    print("\n🏁 Test completed!")