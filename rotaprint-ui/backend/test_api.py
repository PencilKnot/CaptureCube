#!/usr/bin/env python3
"""
API Test Suite for AdGen Studio Backend
Tests all routes with real S3 bucket data
"""

import requests
import json
import sys
from datetime import datetime

# Backend configuration
BASE_URL = "http://localhost:8000"
TEST_BUCKET = "htn-test-bucket"  # Will be set dynamically from available buckets

def print_header(title):
    """Print a formatted test section header"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_result(test_name, success, data=None, error=None):
    """Print formatted test results"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")

    if success and data:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list) and len(value) > 3:
                    print(f"   📊 {key}: [{len(value)} items] {value[:3]}...")
                elif isinstance(value, str) and len(value) > 80:
                    print(f"   📊 {key}: {value[:80]}...")
                else:
                    print(f"   📊 {key}: {value}")
        else:
            print(f"   📊 Response: {data}")

    if error:
        print(f"   ❌ Error: {error}")
    print("-" * 40)

def test_health_check():
    """Test the health check endpoint"""
    print_header("Health Check Test")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print_result("Health Check", True, {
                "status": data.get("status"),
                "timestamp": data.get("timestamp"),
                "response_time": f"{response.elapsed.total_seconds():.3f}s"
            })
            return True
        else:
            print_result("Health Check", False, error=f"Status code: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Health Check", False, error=str(e))
        return False

def test_list_buckets():
    """Test listing S3 buckets"""
    print_header("List S3 Buckets Test")

    try:
        response = requests.get(f"{BASE_URL}/api/s3/buckets", timeout=30)

        if response.status_code == 200:
            data = response.json()
            buckets = data.get("buckets", [])

            if buckets:
                print_result("List Buckets", True, {
                    "bucket_count": len(buckets),
                    "buckets": buckets,
                    "selected_test_bucket": TEST_BUCKET
                })
                return True
            else:
                print_result("List Buckets", False, error="No buckets found")
                return False
        else:
            print_result("List Buckets", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("List Buckets", False, error=str(e))
        return False

def test_list_directories():
    """Test listing directories in S3 bucket"""
    print_header("List S3 Directories Test")

    if not TEST_BUCKET:
        print_result("List Directories", False, error="No test bucket available")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/api/s3/directories",
            params={"bucket": TEST_BUCKET},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            directories = data.get("directories", [])

            print_result("List Directories", True, {
                "bucket": TEST_BUCKET,
                "directory_count": len(directories),
                "directories": directories
            })
            return True
        else:
            print_result("List Directories", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("List Directories", False, error=str(e))
        return False

def test_latest_directory():
    """Test getting the latest directory"""
    print_header("Get Latest Directory Test")

    if not TEST_BUCKET:
        print_result("Latest Directory", False, error="No test bucket available")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/api/s3/latest-directory",
            params={"bucket": TEST_BUCKET},
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()

            print_result("Latest Directory", True, {
                "bucket": TEST_BUCKET,
                "directory": data.get("directory"),
                "last_modified": data.get("last_modified"),
                "image_count": data.get("image_count"),
                "sample_keys": data.get("image_keys", [])[:5] if data.get("image_keys") else []
            })
            return data
        else:
            print_result("Latest Directory", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Latest Directory", False, error=str(e))
        return False

def test_download_directory(latest_dir_data):
    """Test downloading directory images"""
    print_header("Download Directory Images Test")

    if not TEST_BUCKET or not latest_dir_data:
        print_result("Download Directory", False, error="No test bucket or directory data available")
        return False

    directory = latest_dir_data.get("directory")
    if not directory:
        print_result("Download Directory", False, error="No directory found in latest directory data")
        return False

    try:
        payload = {
            "bucket": TEST_BUCKET,
            "directory": directory
        }

        response = requests.post(
            f"{BASE_URL}/api/s3/download-directory",
            json=payload,
            timeout=120  # Longer timeout for downloads
        )

        if response.status_code == 200:
            data = response.json()

            print_result("Download Directory", True, {
                "status": data.get("status"),
                "directory": data.get("directory"),
                "downloaded_count": data.get("downloaded_count"),
                "temp_directory": data.get("temp_directory"),
                "sample_files": data.get("files", [])[:3] if data.get("files") else []
            })
            return True
        else:
            print_result("Download Directory", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Download Directory", False, error=str(e))
        return False

def test_image_keys_validation(latest_dir_data):
    """Test image keys validation"""
    print_header("Image Keys Validation Test")

    if not TEST_BUCKET or not latest_dir_data:
        print_result("Image Keys Validation", False, error="No test bucket or directory data available")
        return False

    image_keys = latest_dir_data.get("image_keys", [])
    if not image_keys:
        print_result("Image Keys Validation", False, error="No image keys found in latest directory")
        return False

    # Test with mix of valid and invalid keys
    test_keys = image_keys[:3] if len(image_keys) >= 3 else image_keys
    test_keys.append("nonexistent/fake-image.jpg")  # Add invalid key

    try:
        payload = {
            "bucket": TEST_BUCKET,
            "keys": test_keys
        }

        response = requests.post(
            f"{BASE_URL}/api/s3/image-keys",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()

            print_result("Image Keys Validation", True, {
                "test_keys_count": len(test_keys),
                "valid_count": data.get("valid_count"),
                "invalid_count": data.get("invalid_count"),
                "valid_keys": data.get("valid_keys"),
                "invalid_keys": data.get("invalid_keys")
            })
            return True
        else:
            print_result("Image Keys Validation", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Image Keys Validation", False, error=str(e))
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print_header("Error Handling Tests")

    # Test missing bucket parameter
    response = requests.get(f"{BASE_URL}/api/s3/directories", timeout=10)
    success1 = response.status_code == 400
    print_result("Missing Bucket Parameter", success1, {"status_code": response.status_code})

    # Test invalid bucket name
    response = requests.get(f"{BASE_URL}/api/s3/directories", params={"bucket": "nonexistent-bucket-12345"}, timeout=10)
    success2 = response.status_code == 500  # Should return error
    print_result("Invalid Bucket Name", success2, {"status_code": response.status_code})

    # Test invalid JSON payload
    response = requests.post(f"{BASE_URL}/api/s3/image-keys", data="invalid json", timeout=10)
    success3 = response.status_code == 400
    print_result("Invalid JSON Payload", success3, {"status_code": response.status_code})

    return success1 and success2 and success3

def main():
    """Run all tests"""
    print("🚀 Starting AdGen Studio Backend API Tests")
    print(f"📍 Testing against: {BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")

    # Track test results
    test_results = []

    # Run tests in sequence
    test_results.append(("Health Check", test_health_check()))
    test_results.append(("List Buckets", test_list_buckets()))
    test_results.append(("List Directories", test_list_directories()))

    latest_dir_data = test_latest_directory()
    test_results.append(("Latest Directory", bool(latest_dir_data)))

    if latest_dir_data:
        test_results.append(("Download Directory", test_download_directory(latest_dir_data)))
        test_results.append(("Image Keys Validation", test_image_keys_validation(latest_dir_data)))
    else:
        test_results.append(("Download Directory", False))
        test_results.append(("Image Keys Validation", False))

    test_results.append(("Error Handling", test_error_handling()))

    # Print summary
    print_header("Test Summary")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    print(f"📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")

    if TEST_BUCKET:
        print(f"🗂️  Test Bucket Used: {TEST_BUCKET}")

    print(f"⏰ Test completed at: {datetime.now().isoformat()}")

    # Print detailed results
    print("\nDetailed Results:")
    for test_name, result in test_results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")

    # Exit with appropriate code
    exit_code = 0 if passed == total else 1
    print(f"\n🏁 Tests completed with exit code: {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        sys.exit(1)