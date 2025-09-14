#!/usr/bin/env python3
"""
Flask Backend Runner
Run this script to start the AdGen Studio backend server
"""

from app import app

if __name__ == '__main__':
    print("🚀 Starting AdGen Studio Backend...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔍 Health check: http://localhost:5000/health")
    print("📊 API Documentation:")
    print("   - GET  /api/s3/buckets - List available S3 buckets")
    print("   - GET  /api/s3/directories?bucket=<name> - List directories in bucket")
    print("   - GET  /api/s3/latest-directory?bucket=<name> - Get latest directory")
    print("   - POST /api/s3/download-directory - Download directory images")
    print("   - POST /api/s3/image-keys - Validate image keys")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=8000)