"""
FastAPI routes for PDF extraction API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from typing import Optional
import os
import uuid
from datetime import datetime
import asyncio
import logging

from src.models.extraction_result import ExtractResponse, StatusResponse, ExportRequest
from src.utils.validators import PDFValidator
from src.services.pdf_processor import PDFProcessor, PDFProcessingError
from src.services.job_manager import job_manager
from src.services.exporter import MetadataExporter, ExportError


logger = logging.getLogger(__name__)
router = APIRouter(tags=["extraction"])

# In-memory storage for extracted files (TODO: Replace with persistent storage)
extracted_files = {}


@router.post("/extract", response_model=ExtractResponse)
async def upload_and_extract(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Upload a PDF file and start extraction job.
    
    Args:
        file: PDF file to extract metadata from
        background_tasks: FastAPI background tasks
        
    Returns:
        ExtractResponse with job_id for polling
        
    Raises:
        HTTPException: 400 for invalid files, 413 for oversized files
    """
    try:
        # Validate filename
        if not PDFValidator.validate_filename(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF files are supported."
            )
        
        # Read and validate file size
        content = await file.read()
        file_size = len(content)
        
        if not PDFValidator.validate_file_size(file_size):
            error_msg = PDFValidator.get_size_error_message(file_size)
            raise HTTPException(
                status_code=413,
                detail=f"File too large. {error_msg}"
            )
        
        # Save file temporarily
        temp_dir = "/tmp/uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        pdf_id = str(uuid.uuid4())
        temp_path = os.path.join(temp_dir, f"{pdf_id}.pdf")
        
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # Create extraction job
        job_id = str(uuid.uuid4())
        job = job_manager.create_job(
            job_id=job_id,
            pdf_id=pdf_id,
            temp_path=temp_path,
            filename=file.filename
        )
        
        # Start extraction in background
        if background_tasks:
            background_tasks.add_task(job_manager.start_extraction, job_id)
        else:
            # Fallback: create task without background_tasks
            asyncio.create_task(job_manager.start_extraction(job_id))
        
        logger.info(f"Created extraction job {job_id} for {file.filename}")
        
        return ExtractResponse(
            job_id=job_id,
            status="pending",
            pdf_id=pdf_id,
            poll_interval_ms=1000
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process uploaded file"
        )


@router.get("/extract/{job_id}", response_model=StatusResponse)
async def get_extraction_status(job_id: str):
    """
    Get current status of an extraction job.
    
    Args:
        job_id: The extraction job ID
        
    Returns:
        StatusResponse with current status and metadata if complete
        
    Raises:
        HTTPException: 404 if job not found
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Extraction job {job_id} not found"
        )
    
    status_info = job_manager.get_status(job_id)
    
    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        elapsed_ms=status_info.get("elapsed_ms", 0),
        metadata=job.get("metadata"),
        error=job.get("error")
    )


@router.post("/export")
async def export_metadata(request: ExportRequest):
    """
    Generate export files for extracted metadata.
    
    Args:
        request: Export request containing metadata_id, formats, and options
        
    Returns:
        Export information with download URLs
    """
    try:
        metadata_id = request.metadata_id
        formats = request.formats
        include_confidence = request.include_confidence
        
        # Find metadata from any extraction job
        metadata = None
        for job in job_manager.jobs.values():
            if job.get("metadata") and job["metadata"].id == metadata_id:
                metadata = job["metadata"]
                break
        
        if not metadata:
            raise HTTPException(
                status_code=404,
                detail=f"Metadata {metadata_id} not found"
            )
        
        # Generate files in requested formats
        export_id = str(uuid.uuid4())
        files = {}
        
        for fmt in formats:
            if fmt == "json":
                content = MetadataExporter.to_json(metadata, include_confidence)
                files[fmt] = f"metadata-{export_id}.json"
            elif fmt == "xml":
                content = MetadataExporter.to_xml(metadata, include_confidence)
                files[fmt] = f"metadata-{export_id}.xml"
            elif fmt == "toon":
                content = MetadataExporter.to_toon(metadata, include_confidence)
                files[fmt] = f"metadata-{export_id}.toon"
            else:
                logger.warning(f"Unknown export format: {fmt}")
                continue
            
            # Store content in memory (TODO: Replace with file storage)
            extracted_files[files[fmt]] = content
        
        logger.info(f"Generated exports {export_id} in formats: {', '.join(formats)}")
        
        return {
            "export_id": export_id,
            "metadata_id": metadata_id,
            "formats": list(files.keys()),
            "files": files
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating exports: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate export files"
        )


@router.get("/download/{export_id}/{format_type}")
async def download_file(export_id: str, format_type: str):
    """
    Download exported file.
    
    Args:
        export_id: ID of export
        format_type: File format (json, xml, toon)
        
    Returns:
        File content for download
        
    Raises:
        HTTPException: 404 if file not found
    """
    try:
        # Map format to filename
        filename = f"metadata-{export_id}.{format_type}"
        
        if filename not in extracted_files:
            raise HTTPException(
                status_code=404,
                detail=f"Export file not found: {filename}"
            )
        
        content = extracted_files[filename]
        
        # Set appropriate MIME type
        mime_types = {
            "json": "application/json",
            "xml": "application/xml",
            "toon": "text/plain"
        }
        
        mime_type = mime_types.get(format_type, "application/octet-stream")
        
        logger.info(f"Downloading export file: {filename}")
        
        return StreamingResponse(
            iter([content]),
            media_type=mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to download file"
        )
