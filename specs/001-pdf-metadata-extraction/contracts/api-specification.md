# API Contracts: PDF Metadata Extraction

**Phase**: 1 (Design & Contracts)  
**Date**: 2026-05-04  
**Status**: Complete

---

## Overview

This document defines the REST API contracts between the React frontend and Python FastAPI backend. All endpoints use JSON request/response format (except multipart for file uploads).

**Base URL**: `http://localhost:8000/api` (local development)  
**API Version**: v1

---

## Endpoint 1: Health Check

Monitor backend service health.

### Request

```
GET /health
```

**Headers**: None required

**Parameters**: None

### Response

**Success (200 OK)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-04T14:30:00Z",
  "services": {
    "ollama": "connected",
    "pdf_processor": "ready"
  }
}
```

**Failure (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "error": "Ollama service unavailable",
  "timestamp": "2026-05-04T14:30:00Z"
}
```

---

## Endpoint 2: Upload and Extract Metadata

Submit a PDF file for metadata extraction.

### Request

```
POST /extract
Content-Type: multipart/form-data
```

**Headers**:
- `Content-Type: multipart/form-data` (automatic with file upload)

**Form Parameters**:
```
{
  "file": <binary PDF data>,          // Required, PDF file
  "filename": "paper.pdf"             // Optional, original filename
}
```

**Example (curl)**:
```bash
curl -X POST http://localhost:8000/api/extract \
  -F "file=@paper.pdf" \
  -F "filename=paper.pdf"
```

### Response

**Success (202 Accepted)**: Extraction job created
```json
{
  "job_id": "job_550e8400_e29b_41d4_a716_446655440000",
  "status": "pending",
  "pdf_id": "pdf_550e8400_e29b_41d4_a716_446655440001",
  "message": "Extraction started. Poll the status endpoint for results.",
  "poll_interval_ms": 1000
}
```

**Validation Error (400 Bad Request)**:
```json
{
  "error": "INVALID_FILE_FORMAT",
  "message": "Uploaded file is not a valid PDF",
  "details": "PDF header signature not found"
}
```

**File Too Large (413 Payload Too Large)**:
```json
{
  "error": "FILE_TOO_LARGE",
  "message": "Maximum file size is 50MB",
  "max_size_mb": 50
}
```

**Server Error (500 Internal Server Error)**:
```json
{
  "error": "PDF_PROCESSING_ERROR",
  "message": "Failed to process PDF file",
  "details": "pdfplumber error: ..."
}
```

---

## Endpoint 3: Poll Extraction Status

Check the status of an ongoing extraction job.

### Request

```
GET /extract/{job_id}
```

**Path Parameters**:
- `job_id` (string, required): Job ID from POST /extract response

**Query Parameters**: None

**Headers**: None required

**Example**:
```
GET /extract/job_550e8400_e29b_41d4_a716_446655440000
```

### Response

**Pending (200 OK)**:
```json
{
  "job_id": "job_550e8400_e29b_41d4_a716_446655440000",
  "status": "processing",
  "started_at": "2026-05-04T14:30:00Z",
  "elapsed_ms": 2500,
  "estimated_remaining_ms": 15000
}
```

**Completed Successfully (200 OK)**:
```json
{
  "job_id": "job_550e8400_e29b_41d4_a716_446655440000",
  "status": "completed",
  "started_at": "2026-05-04T14:30:00Z",
  "completed_at": "2026-05-04T14:30:18Z",
  "elapsed_ms": 18000,
  "metadata": {
    "id": "meta_550e8400_e29b_41d4_a716_446655440002",
    "title": "Deep Learning for Scientific Document Analysis",
    "doi": "10.1145/3123456.3456789",
    "abstract": "This paper presents a novel approach to ...",
    "keywords": ["deep learning", "document analysis", "metadata extraction"],
    "authors": [
      {
        "id": "auth_1",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "affiliationIds": ["aff_1"]
      },
      {
        "id": "auth_2",
        "name": "John Doe",
        "email": "john@example.com",
        "affiliationIds": ["aff_1", "aff_2"]
      }
    ],
    "affiliations": [
      {
        "id": "aff_1",
        "institution": "MIT",
        "department": "Computer Science",
        "city": "Cambridge",
        "country": "USA"
      },
      {
        "id": "aff_2",
        "institution": "Stanford University",
        "department": "AI Lab",
        "city": "Stanford",
        "country": "USA"
      }
    ],
    "publication_date": "2024-01-15",
    "journal_name": "ACM Computing Surveys",
    "confidence_scores": {
      "title": 0.98,
      "doi": 0.95,
      "authors": 0.92,
      "affiliations": 0.85,
      "abstract": 0.89,
      "keywords": 0.87,
      "publication_date": 0.93,
      "journal_name": 0.88
    },
    "overall_confidence": 0.91
  }
}
```

**Failed (200 OK with error status)**:
```json
{
  "job_id": "job_550e8400_e29b_41d4_a716_446655440000",
  "status": "failed",
  "error": {
    "code": "EXTRACTION_FAILED",
    "message": "LLM extraction failed after 3 retries",
    "details": "Ollama service timeout"
  },
  "retry_available": true,
  "retry_count": 3
}
```

**Timeout (200 OK with error status)**:
```json
{
  "job_id": "job_550e8400_e29b_41d4_a716_446655440000",
  "status": "timeout",
  "error": {
    "code": "EXTRACTION_TIMEOUT",
    "message": "Extraction exceeded 30 second time limit",
    "details": "LLM inference took too long"
  },
  "retry_available": true,
  "retry_count": 1
}
```

**Job Not Found (404 Not Found)**:
```json
{
  "error": "JOB_NOT_FOUND",
  "message": "No extraction job found with ID: job_invalid_id"
}
```

---

## Endpoint 4: Generate Export Files

Generate JSON, XML, and TOON export files for extracted metadata.

### Request

```
POST /export
Content-Type: application/json
```

**Headers**: None required

**Request Body**:
```json
{
  "metadata_id": "meta_550e8400_e29b_41d4_a716_446655440002",
  "formats": ["json", "xml", "toon"],
  "include_confidence": true,
  "filename_prefix": "research_paper_2024"
}
```

**Parameters**:
- `metadata_id` (string, required): ID of the ExtractedMetadata to export
- `formats` (array of strings, optional): Formats to generate; default: ["json", "xml", "toon"]
- `include_confidence` (boolean, optional): Include confidence scores; default: true
- `filename_prefix` (string, optional): Prefix for generated filenames; default: "metadata"

### Response

**Success (200 OK)**:
```json
{
  "export_id": "exp_550e8400_e29b_41d4_a716_446655440003",
  "metadata_id": "meta_550e8400_e29b_41d4_a716_446655440002",
  "generated_at": "2026-05-04T14:31:00Z",
  "files": {
    "json": {
      "format": "json",
      "filename": "research_paper_2024.json",
      "mime_type": "application/json",
      "file_size": 2048,
      "download_url": "/api/download/exp_550e8400_e29b_41d4_a716_446655440003/json",
      "content": "<base64 encoded or inline content optional>"
    },
    "xml": {
      "format": "xml",
      "filename": "research_paper_2024.xml",
      "mime_type": "application/xml",
      "file_size": 3456,
      "download_url": "/api/download/exp_550e8400_e29b_41d4_a716_446655440003/xml"
    },
    "toon": {
      "format": "toon",
      "filename": "research_paper_2024.toon",
      "mime_type": "text/plain",
      "file_size": 1800,
      "download_url": "/api/download/exp_550e8400_e29b_41d4_a716_446655440003/toon"
    }
  }
}
```

**Metadata Not Found (404 Not Found)**:
```json
{
  "error": "METADATA_NOT_FOUND",
  "message": "No metadata found with ID: meta_invalid_id"
}
```

**Export Error (500 Internal Server Error)**:
```json
{
  "error": "EXPORT_GENERATION_FAILED",
  "message": "Failed to generate export files",
  "details": "XML formatting error"
}
```

---

## Endpoint 5: Download Export File

Download a generated export file.

### Request

```
GET /download/{export_id}/{format}
```

**Path Parameters**:
- `export_id` (string, required): Export ID from POST /export response
- `format` (string, required): File format ("json", "xml", or "toon")

**Headers**: None required

**Example**:
```
GET /download/exp_550e8400_e29b_41d4_a716_446655440003/json
```

### Response

**Success (200 OK)**:
```
Content-Type: application/json (or application/xml or text/plain)
Content-Disposition: attachment; filename="research_paper_2024.json"

<file binary content>
```

**File Not Found (404 Not Found)**:
```json
{
  "error": "FILE_NOT_FOUND",
  "message": "Export file not found"
}
```

---

## Error Response Format

All error responses follow this standard format:

```json
{
  "error": "<ERROR_CODE>",
  "message": "<user-friendly message>",
  "details": "<technical details (optional)>",
  "timestamp": "2026-05-04T14:30:00Z",
  "request_id": "<correlation ID for debugging>"
}
```

### HTTP Status Codes

| Code | Meaning | Scenarios |
|------|---------|-----------|
| 200 | OK | Successful response with data |
| 202 | Accepted | Job created, polling required |
| 400 | Bad Request | Invalid input, validation failed |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File exceeds size limit |
| 422 | Unprocessable Entity | Semantic error (e.g., corrupt PDF) |
| 500 | Internal Server Error | Server error, retry recommended |
| 503 | Service Unavailable | Backend service (Ollama) unavailable |

---

## Request/Response Size Limits

- **Maximum request body**: 55 MB (accounting for HTTP overhead)
- **Maximum response body**: 10 MB
- **Timeout for all endpoints**: 35 seconds (except /extract which uses 30s LLM timeout + 5s buffer)

---

## Rate Limiting (Future)

Not implemented for v1 (single-user), but prepared for:
- Per-user extraction: 10 jobs/minute
- Per-user export: 20 exports/hour
- Global: 100 concurrent extraction jobs

---

## Security Considerations

- **HTTPS**: Required for production (use TLS 1.3+)
- **CORS**: Configure to allow frontend origin only
- **Input Validation**: All file uploads scanned for malicious content
- **Request Signing**: Consider adding HMAC signature for production
- **API Keys**: Future enhancement for multi-user access control

---

## API Version Management

- **Current Version**: v1
- **Deprecation Policy**: 2 API versions supported simultaneously
- **Migration Path**: Breaking changes announced 3 months in advance

---

## Client Implementation Notes

### Frontend (React)
```typescript
// Example: Extract metadata
const response = await fetch('/api/extract', {
  method: 'POST',
  body: formData,  // file + filename
});

const { job_id } = await response.json();

// Poll for status
const pollInterval = setInterval(async () => {
  const statusResponse = await fetch(`/api/extract/${job_id}`);
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    // Display metadata
    clearInterval(pollInterval);
  }
}, 1000);
```

### Backend (Python/FastAPI)
- See `backend/src/api/routes.py` for implementation
- Use Pydantic models for request/response validation
- Implement structured logging with correlation IDs
- Add health checks to dependency injection

---

## Testing Strategy

- **Contract Tests**: Verify request/response schema compliance
- **Integration Tests**: Test full workflows (upload → extract → export)
- **Load Tests**: Verify performance under concurrent requests
- **Error Scenarios**: Verify all error codes and messages are correct

See `tasks.md` for testing implementation details.
