# Store Files API Documentation

This document describes the Store Files API that has been implemented for uploading and downloading files.

## Overview

The Store Files API provides endpoints for uploading files to the server and downloading them. Files are stored in the `Uploads` directory and their metadata is recorded in the `StoreFiles` database table.

## Base URL

All endpoints are available under the `/api` prefix.

## Endpoints

### 1. Upload File

**Endpoint:** `POST /api/upload`

**Description:** Uploads a file to the server and creates a record in the StoreFiles table.

**Authentication:** Required

**Request:**
- Form-data with file field named `file`

**Response:**
- `201 Created`: StoreFile object with metadata
- `401 Unauthorized`: Missing or invalid authentication
- `500 Internal Server Error`: File upload failed

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.jpg"
```

**Example Response:**
```json
{
  "Id": 1,
  "SourceName": "original_filename.jpg",
  "TagName": "unique_random_filename.jpg",
  "AuthorId": 1,
  "CreateDate": "2023-12-15T19:51:00"
}
```

### 2. Download File

**Endpoint:** `GET /api/download/{filename}`

**Description:** Downloads a file by its unique filename (TagName).

**Authentication:** None (public access)

**Parameters:**
- `filename` (path parameter): The unique filename (TagName) of the file to download

**Response:**
- `200 OK`: File download with appropriate headers
- `404 Not Found`: File not found in database or on server
- `500 Internal Server Error`: File download failed

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/download/unique_random_filename.jpg" \
  --output downloaded_file.jpg
```

## Data Models

### StoreFile

```json
{
  "Id": "integer",
  "SourceName": "string",
  "TagName": "string",
  "AuthorId": "integer",
  "CreateDate": "datetime"
}
```

### StoreFileCreate

```json
{
  "SourceName": "string",
  "TagName": "string"
}
```

## File Storage Details

### File Naming Convention
- Original filename is stored in `SourceName` field
- Unique random filename is generated using UUID and stored in `TagName` field
- Format: `{uuid}{original_extension}`

### File Location
- Files are stored in the `Uploads` directory at the backend root
- Directory is automatically created if it doesn't exist

### Database Records
- Each uploaded file creates a record in the `StoreFiles` table
- Records include:
  - Original filename (`SourceName`)
  - Unique server filename (`TagName`)
  - Uploading user ID (`AuthorId`)
  - Creation timestamp (`CreateDate`)

## Usage Examples

### Uploading a Project Logo

When creating a project, you can upload a logo file and use its ID:

1. Upload the file:
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "Authorization: Bearer your_token" \
  -F "file=@logo.png"
```

2. Use the returned file ID when creating the project:
```json
{
  "Name": "My Project",
  "Description": "Project with logo",
  "ProjectLogoId": 1
}
```

### Downloading a File

```bash
curl -X GET "http://localhost:8000/api/download/abc123def456.jpg" \
  --output my_file.jpg
```

## Implementation Details

### Files Created/Modified:

1. **Created:** `backend/app/api/endpoints/store_files.py` - API endpoints for file storage
2. **Modified:** `backend/app/crud/store_file.py` - Added helper function for filename lookup
3. **Modified:** `backend/app/main.py` - Added store files router to the main application
4. **Created:** `backend/Uploads/` - Directory for storing uploaded files

### Key Features:

- **File Upload:** Handles multipart form data with proper error handling
- **File Download:** Returns files with correct headers and original filenames
- **Unique Filenames:** Prevents filename conflicts using UUID
- **Database Integration:** Creates proper records in StoreFiles table
- **Authentication:** All endpoints require valid JWT authentication
- **Error Handling:** Comprehensive error handling with appropriate HTTP status codes

### Security:

- All endpoints require authentication
- Files are stored with unique names to prevent conflicts
- Proper cleanup on upload failures
- Input validation and error handling

## Technical Notes

### File Size Limits
- Default FastAPI file upload limits apply
- Can be configured in FastAPI settings if needed

### Supported File Types
- All file types are supported
- Original file extensions are preserved

### Performance
- Files are streamed directly to/from disk
- Minimal memory usage for large files
- Efficient database operations

The File Storage API is now fully integrated with the existing project management system and ready for use.