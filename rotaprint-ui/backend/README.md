# AdGen Studio Backend

Flask backend for the AdGen Studio application with S3 integration.

## Setup

1. **Create Virtual Environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**:
   ```bash
   python run.py
   ```

## API Endpoints

### Health Check
- **GET** `/health` - Server health status

### S3 Operations
- **GET** `/api/s3/buckets` - List all S3 buckets
- **GET** `/api/s3/directories?bucket=<name>` - List directories in bucket
- **GET** `/api/s3/latest-directory?bucket=<name>` - Get latest directory with images
- **POST** `/api/s3/download-directory` - Download images from directory
- **POST** `/api/s3/image-keys` - Validate S3 image keys

### Example Usage

#### Get Latest Directory:
```bash
curl "http://localhost:5000/api/s3/latest-directory?bucket=your-bucket-name"
```

#### Download Directory Images:
```bash
curl -X POST http://localhost:5000/api/s3/download-directory \
  -H "Content-Type: application/json" \
  -d '{"bucket": "your-bucket-name", "directory": "photos/2024-01"}'
```

## Features

✅ **S3 Bucket Listing** - Browse available buckets
✅ **Directory Discovery** - Find photo directories
✅ **Latest Directory Detection** - Automatically find newest photos
✅ **Image Download** - Download images to temp directory
✅ **Image Validation** - Verify S3 keys exist and are images
✅ **CORS Support** - Ready for frontend integration
✅ **Error Handling** - Comprehensive error responses

## Next Steps

- [ ] Add image-to-video generation API integration (Gemini)
- [ ] Add video storage and serving
- [ ] Add project/campaign management endpoints
- [ ] Add authentication/authorization
- [ ] Add file upload to S3 functionality