#!/usr/bin/env python3
"""
Test Google Cloud Authentication and Permissions
"""

import os
from dotenv import load_dotenv
from google.auth import default
from google.auth.transport.requests import Request
from google.cloud import storage
import requests

# Load environment variables
load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", "htn-scanner")

def test_authentication():
    """Test Google Cloud authentication"""
    print("🔐 Testing Google Cloud Authentication")
    print("-" * 50)

    try:
        # Test default credentials
        creds, project = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        print(f"✅ Default credentials found")
        print(f"📍 Project from credentials: {project}")
        print(f"📍 Project from env: {PROJECT_ID}")

        # Refresh credentials
        creds.refresh(Request())
        access_token = creds.token
        print(f"✅ Access token obtained (length: {len(access_token)})")

        return access_token, creds

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None, None

def test_storage_access(creds):
    """Test Google Cloud Storage access"""
    print("\n📦 Testing Google Cloud Storage Access")
    print("-" * 50)

    try:
        # Test GCS client
        client = storage.Client(project=PROJECT_ID, credentials=creds)

        # List buckets
        buckets = list(client.list_buckets())
        print(f"✅ Found {len(buckets)} GCS buckets")

        for bucket in buckets:
            print(f"   📂 {bucket.name}")

        # Check for required bucket
        required_bucket = "htn-bucket-test"
        bucket_names = [b.name for b in buckets]

        if required_bucket in bucket_names:
            print(f"✅ Required bucket '{required_bucket}' exists")
        else:
            print(f"❌ Required bucket '{required_bucket}' not found")
            print(f"   Available buckets: {bucket_names}")

        return True

    except Exception as e:
        print(f"❌ Storage access failed: {e}")
        return False

def test_vertex_ai_access(access_token):
    """Test Vertex AI API access"""
    print("\n🧠 Testing Vertex AI API Access")
    print("-" * 50)

    try:
        # Test Vertex AI endpoint
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/endpoints"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"✅ Vertex AI API accessible")
            data = response.json()
            print(f"📊 Response: {len(str(data))} characters")
        elif response.status_code == 403:
            print(f"❌ Permission denied (403)")
            print(f"   Response: {response.text}")
            print(f"   This suggests the service account lacks Vertex AI permissions")
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Vertex AI API test failed: {e}")
        return False

def test_veo_model_access(access_token):
    """Test Veo model specific access"""
    print("\n🎬 Testing Veo Model Access")
    print("-" * 50)

    try:
        # Test Veo model endpoint (just a GET to check permissions)
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            print(f"✅ Veo model endpoint accessible")
        elif response.status_code == 403:
            print(f"❌ Permission denied for Veo model (403)")
            print(f"   Response: {response.text}")
        else:
            print(f"⚠️  Response: {response.status_code}")
            print(f"   Response: {response.text}")

        return response.status_code == 200

    except Exception as e:
        print(f"❌ Veo model test failed: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for common permission issues"""
    print("\n🔧 Permission Fix Suggestions")
    print("-" * 50)
    print("If you're getting 403 errors, try these steps:")
    print()
    print("1. **Service Account Permissions:**")
    print("   - Vertex AI User")
    print("   - Storage Admin (or Storage Object Admin)")
    print("   - Cloud Storage Service Agent")
    print()
    print("2. **Enable APIs:**")
    print("   gcloud services enable aiplatform.googleapis.com")
    print("   gcloud services enable storage-api.googleapis.com")
    print()
    print("3. **Authentication Setup:**")
    print("   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json")
    print("   # OR use gcloud auth application-default login")
    print()
    print("4. **Veo API Access:**")
    print("   - Veo is still in preview, you may need to request access")
    print("   - Check if your project has been allowlisted for Veo")

if __name__ == "__main__":
    print("🚀 Google Cloud Permission Diagnostic")
    print("=" * 60)
    print(f"📍 Project ID: {PROJECT_ID}")
    print(f"📍 Required GCS Bucket: htn-bucket-test")
    print()

    # Test authentication
    access_token, creds = test_authentication()

    if not access_token:
        print("\n❌ Cannot proceed without authentication")
        suggest_fixes()
        exit(1)

    # Test storage access
    storage_ok = test_storage_access(creds)

    # Test Vertex AI access
    vertex_ai_ok = test_vertex_ai_access(access_token)

    # Test Veo model access
    veo_ok = test_veo_model_access(access_token)

    # Summary
    print("\n📊 Test Summary")
    print("-" * 30)
    print(f"Authentication: {'✅' if access_token else '❌'}")
    print(f"Storage Access: {'✅' if storage_ok else '❌'}")
    print(f"Vertex AI: {'✅' if vertex_ai_ok else '❌'}")
    print(f"Veo Model: {'✅' if veo_ok else '❌'}")

    if not (vertex_ai_ok and veo_ok):
        suggest_fixes()