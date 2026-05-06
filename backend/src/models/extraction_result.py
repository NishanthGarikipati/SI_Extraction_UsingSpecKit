"""
Models for extraction jobs and API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from .metadata import ExtractedMetadata


class ExtractionJob(BaseModel):
    """Represents a PDF metadata extraction job."""
    id: str = Field(..., description="Unique job ID")
    pdf_document_id: str = Field(..., description="Associated PDF document ID")
    status: Literal["pending", "processing", "completed", "failed", "timeout"] = Field(
        default="pending",
        description="Current job status"
    )
    start_time: Optional[datetime] = Field(None, description="When extraction started")
    end_time: Optional[datetime] = Field(None, description="When extraction completed")
    elapsed_time_ms: int = Field(default=0, description="Elapsed time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if extraction failed")
    llm_model: str = Field(default="llama2", description="LLM model used")
    retry_count: int = Field(default=0, ge=0, le=3, description="Number of retries attempted")
    raw_llm_output: Optional[str] = Field(None, description="Raw output from LLM before parsing")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "job-12345",
                "pdf_document_id": "pdf-001",
                "status": "processing",
                "start_time": "2026-05-04T10:00:00Z",
                "end_time": None,
                "elapsed_time_ms": 5000,
                "error": None,
                "llm_model": "llama2",
                "retry_count": 0,
                "raw_llm_output": None
            }
        }


class ExtractResponse(BaseModel):
    """Response from PDF upload endpoint."""
    job_id: str = Field(..., description="Created extraction job ID")
    status: str = Field(default="pending", description="Initial job status")
    pdf_id: str = Field(..., description="PDF document ID")
    poll_interval_ms: int = Field(default=1000, description="Recommended polling interval")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job-12345",
                "status": "pending",
                "pdf_id": "pdf-001",
                "poll_interval_ms": 1000
            }
        }


class StatusResponse(BaseModel):
    """Response from extraction status polling endpoint."""
    status: str = Field(..., description="Current extraction status")
    elapsed_time_ms: int = Field(default=0, description="Time spent extracting")
    estimated_remaining_ms: Optional[int] = Field(None, description="Estimated time remaining")
    metadata: Optional[ExtractedMetadata] = Field(None, description="Extracted metadata (if completed)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    retry_available: bool = Field(default=True, description="Whether retry is available")
    retry_count: int = Field(default=0, description="Number of retries used")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "processing",
                "elapsed_time_ms": 5000,
                "estimated_remaining_ms": 15000,
                "metadata": None,
                "error": None,
                "retry_available": True,
                "retry_count": 0
            }
        }


class PDFDocument(BaseModel):
    """Represents an uploaded PDF document."""
    id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, le=52428800, description="File size in bytes (max 50MB)")
    upload_timestamp: datetime = Field(..., description="When file was uploaded")
    page_count: Optional[int] = Field(None, description="Number of pages")
    text_content: Optional[str] = Field(None, description="Extracted text content")
    storage_location: str = Field(..., description="Path or location where PDF is stored")
    validation_status: Literal["valid", "invalid"] = Field(default="valid", description="Validation result")
    validation_error: Optional[str] = Field(None, description="Validation error message")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pdf-001",
                "filename": "example.pdf",
                "file_size": 2097152,
                "upload_timestamp": "2026-05-04T10:00:00Z",
                "page_count": 10,
                "text_content": "Sample text...",
                "storage_location": "/tmp/uploads/example.pdf",
                "validation_status": "valid",
                "validation_error": None
            }
        }


class ExportRequest(BaseModel):
    """Request to export metadata."""
    metadata_id: str = Field(..., description="ID of metadata to export")
    formats: list = Field(default=["json"], description="List of formats to export (json, xml, toon)")
    include_confidence: bool = Field(default=True, description="Include confidence scores")
    filename_prefix: Optional[str] = Field(None, description="Custom filename prefix")

    class Config:
        json_schema_extra = {
            "example": {
                "metadata_id": "meta-001",
                "formats": ["json", "xml"],
                "include_confidence": True,
                "filename_prefix": "my_export"
            }
        }


class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="When error occurred")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "file_too_large",
                "message": "PDF file exceeds maximum size of 50MB",
                "details": {"max_size_mb": 50, "uploaded_size_mb": 100},
                "timestamp": "2026-05-04T10:00:00Z",
                "request_id": "req-12345"
            }
        }
