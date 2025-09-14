#!/usr/bin/env python3
"""
Video Generation API Test Suite
Tests the video generation endpoints with real data
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend configuration
BASE_URL = "http://localhost:8000"
TEST_BUCKET = "htn-test-bucket"

def print_header(title):
    """Print a formatted test section header"""
    print("\n" + "=" * 60)
    print(f"🎬 {title}")
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

def test_start_video_generation():
    """Test starting video generation"""
    print_header("Start Video Generation Test")

    # Use sample S3 keys (these should exist in your bucket)
    test_image_keys = [
        "images/sample1.jpg",
        "images/sample2.jpg",
        "images/sample3.jpg"
    ]

    payload = {
        "bucket": TEST_BUCKET,
        "image_keys": test_image_keys,
        "prompt": "Create a dynamic product advertisement showcasing innovation and quality",
        "duration": 8
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/video/generate",
            json=payload,
            timeout=30
        )

        if response.status_code == 202:
            data = response.json()
            generation_id = data.get("generation_id")

            print_result("Start Video Generation", True, {
                "generation_id": generation_id,
                "status": data.get("status"),
                "message": data.get("message")
            })
            return generation_id
        else:
            print_result("Start Video Generation", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print_result("Start Video Generation", False, error=str(e))
        return None

def test_video_generation_status(generation_id):
    """Test getting video generation status"""
    print_header("Video Generation Status Test")

    if not generation_id:
        print_result("Video Generation Status", False, error="No generation ID provided")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/status/{generation_id}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            print_result("Video Generation Status", True, {
                "generation_id": data.get("generation_id"),
                "status": data.get("status"),
                "progress": data.get("progress"),
                "bucket": data.get("bucket"),
                "image_count": data.get("image_count"),
                "started_at": data.get("started_at")
            })
            return data
        else:
            print_result("Video Generation Status", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Video Generation Status", False, error=str(e))
        return False

def test_list_generations():
    """Test listing all video generations"""
    print_header("List Video Generations Test")

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/generations",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            print_result("List Video Generations", True, {
                "total_count": data.get("total_count"),
                "generations": data.get("generations", [])[:3]  # Show first 3
            })
            return True
        else:
            print_result("List Video Generations", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("List Video Generations", False, error=str(e))
        return False

def test_wait_for_completion(generation_id, max_wait_time=300):
    """Wait for video generation to complete"""
    print_header("Wait for Video Completion Test")

    if not generation_id:
        print_result("Wait for Completion", False, error="No generation ID provided")
        return False

    start_time = time.time()
    poll_interval = 10  # seconds

    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(
                f"{BASE_URL}/api/video/status/{generation_id}",
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                progress = data.get("progress", 0)

                print(f"   ⏳ Status: {status}, Progress: {progress}%")

                if status == "completed":
                    print_result("Wait for Completion", True, {
                        "final_status": status,
                        "progress": progress,
                        "total_wait_time": f"{time.time() - start_time:.1f}s"
                    })
                    return data

                elif status == "error":
                    print_result("Wait for Completion", False, error=f"Generation failed with error status")
                    return False

                # Continue waiting
                time.sleep(poll_interval)

            else:
                print(f"   ⚠️ Status check failed: {response.status_code}")
                time.sleep(poll_interval)

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Request error: {str(e)}")
            time.sleep(poll_interval)

    print_result("Wait for Completion", False, error=f"Timeout after {max_wait_time} seconds")
    return False

def test_download_video(generation_id):
    """Test downloading generated video"""
    print_header("Download Video Test")

    if not generation_id:
        print_result("Download Video", False, error="No generation ID provided")
        return False

    try:
        response = requests.get(
            f"{BASE_URL}/api/video/download/{generation_id}",
            timeout=60
        )

        if response.status_code == 200:
            # Save video to file
            filename = f"test_video_{generation_id[:8]}.mp4"
            with open(filename, 'wb') as f:
                f.write(response.content)

            print_result("Download Video", True, {
                "filename": filename,
                "file_size": f"{len(response.content)} bytes",
                "content_type": response.headers.get("content-type")
            })
            return True
        else:
            print_result("Download Video", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Download Video", False, error=str(e))
        return False

def test_cleanup_generation(generation_id):
    """Test cleaning up video generation"""
    print_header("Cleanup Video Generation Test")

    if not generation_id:
        print_result("Cleanup Generation", False, error="No generation ID provided")
        return False

    try:
        response = requests.delete(
            f"{BASE_URL}/api/video/cleanup/{generation_id}",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()

            print_result("Cleanup Generation", True, {
                "message": data.get("message")
            })
            return True
        else:
            print_result("Cleanup Generation", False, error=f"Status code: {response.status_code}, Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_result("Cleanup Generation", False, error=str(e))
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print_header("Video API Error Handling Tests")

    # Test missing required fields
    response = requests.post(f"{BASE_URL}/api/video/generate", json={}, timeout=10)
    success1 = response.status_code == 400
    print_result("Missing Required Fields", success1, {"status_code": response.status_code})

    # Test invalid generation ID
    response = requests.get(f"{BASE_URL}/api/video/status/invalid-id", timeout=10)
    success2 = response.status_code == 404
    print_result("Invalid Generation ID", success2, {"status_code": response.status_code})

    # Test download non-existent video
    response = requests.get(f"{BASE_URL}/api/video/download/invalid-id", timeout=10)
    success3 = response.status_code == 404
    print_result("Download Non-existent Video", success3, {"status_code": response.status_code})

    return success1 and success2 and success3

def main():
    """Run all video generation tests"""
    print("🎬 Starting Video Generation API Tests")
    print(f"📍 Testing against: {BASE_URL}")
    print(f"🗂️  Using bucket: {TEST_BUCKET}")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")

    # Track test results
    test_results = []

    # Run basic API tests
    test_results.append(("List Generations", test_list_generations()))

    # Start video generation
    generation_id = test_start_video_generation()
    test_results.append(("Start Video Generation", bool(generation_id)))

    if generation_id:
        # Test status checking
        test_results.append(("Video Generation Status", bool(test_video_generation_status(generation_id))))

        # Wait for completion (this will take several minutes)
        print("\n🕐 This test may take 5-10 minutes for video generation...")
        completion_data = test_wait_for_completion(generation_id, max_wait_time=600)  # 10 minutes
        test_results.append(("Wait for Completion", bool(completion_data)))

        if completion_data:
            # Test download
            test_results.append(("Download Video", test_download_video(generation_id)))

            # Test cleanup
            test_results.append(("Cleanup Generation", test_cleanup_generation(generation_id)))
        else:
            test_results.append(("Download Video", False))
            test_results.append(("Cleanup Generation", False))

    else:
        test_results.append(("Video Generation Status", False))
        test_results.append(("Wait for Completion", False))
        test_results.append(("Download Video", False))
        test_results.append(("Cleanup Generation", False))

    # Test error handling
    test_results.append(("Error Handling", test_error_handling()))

    # Print summary
    print_header("Video API Test Summary")
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    print(f"📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")

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