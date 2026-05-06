"""
Extraction job lifecycle management
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

from src.models.extraction_result import ExtractionJob
from src.models.metadata import ExtractedMetadata
from src.services.pdf_processor import PDFProcessor, PDFProcessingError
from src.services.rag_extractor import RAGExtractor, ExtractionTimeoutError, MetadataExtractionError


logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Extraction job status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class JobManager:
    """Manages extraction job lifecycle and state."""
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.rag_extractor = RAGExtractor()
    
    def create_job(
        self,
        job_id: str,
        pdf_id: str,
        temp_path: str,
        filename: str
    ) -> ExtractionJob:
        """Create a new extraction job."""
        job_data = {
            "id": job_id,
            "pdf_id": pdf_id,
            "temp_path": temp_path,
            "filename": filename,
            "status": JobStatus.PENDING,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "metadata": None,
            "retry_count": 0,
            "raw_llm_output": None,
            "task": None,  # asyncio Task
        }
        self.jobs[job_id] = job_data
        logger.info(f"Created extraction job {job_id}")
        return self._to_extraction_job(job_data)
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job by ID."""
        return self.jobs.get(job_id)
    
    async def start_extraction(self, job_id: str) -> None:
        """
        Start extraction for a job.
        Runs in background and updates job state.
        """
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job not found: {job_id}")
            return
        
        try:
            job["status"] = JobStatus.PROCESSING
            job["started_at"] = datetime.utcnow()
            logger.info(f"Starting extraction for job {job_id}")
            
            # Extract text from PDF
            text_content, page_count = PDFProcessor.extract_text(job["temp_path"])
            pdf_metadata = PDFProcessor.extract_metadata(job["temp_path"])
            
            # Extract metadata using RAG
            metadata = await self.rag_extractor.extract_metadata_async(
                text_content=text_content,
                job_id=job_id,
                retry_count=0,
                max_retries=3,
                pdf_metadata=pdf_metadata
            )
            
            job["metadata"] = metadata
            job["status"] = JobStatus.COMPLETED
            job["completed_at"] = datetime.utcnow()
            logger.info(f"Extraction completed for job {job_id}")
            
        except ExtractionTimeoutError as e:
            job["status"] = JobStatus.TIMEOUT
            job["error"] = str(e)
            job["retry_count"] += 1
            logger.error(f"Extraction timeout for job {job_id}: {str(e)}")
            
        except MetadataExtractionError as e:
            if job["retry_count"] < 3:
                job["retry_count"] += 1
                logger.warning(f"Extraction failed, retry {job['retry_count']}/3: {str(e)}")
                # Schedule retry
                await asyncio.sleep(2 ** job["retry_count"])
                await self.start_extraction(job_id)
            else:
                job["status"] = JobStatus.FAILED
                job["error"] = str(e)
                logger.error(f"Extraction failed after retries for job {job_id}: {str(e)}")
                
        except PDFProcessingError as e:
            job["status"] = JobStatus.FAILED
            job["error"] = f"PDF processing error: {str(e)}"
            logger.error(f"PDF processing failed for job {job_id}: {str(e)}")
            
        except Exception as e:
            job["status"] = JobStatus.FAILED
            job["error"] = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error in extraction for job {job_id}: {str(e)}", exc_info=True)
    
    def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current status of a job.
        
        Returns:
            Dictionary with status information
        """
        job = self.get_job(job_id)
        if not job:
            return {"status": "not_found", "error": f"Job {job_id} not found"}
        
        now = datetime.utcnow()
        started = job.get("started_at")
        completed = job.get("completed_at")
        
        elapsed_ms = 0
        remaining_ms = None
        
        if started:
            if completed:
                elapsed_ms = int((completed - started).total_seconds() * 1000)
            else:
                elapsed_ms = int((now - started).total_seconds() * 1000)
                # Estimate remaining time if processing
                if job["status"] == JobStatus.PROCESSING:
                    # Typical extraction takes 10-20 seconds
                    remaining_ms = max(0, 20000 - elapsed_ms)
        
        current_status = job["status"].value if isinstance(job["status"], JobStatus) else job["status"]
        return {
            "job_id": job_id,
            "status": current_status,
            "elapsed_ms": elapsed_ms,
            "estimated_remaining_ms": remaining_ms,
            "metadata": job.get("metadata"),
            "error": job.get("error"),
            "retry_count": job.get("retry_count", 0),
            "retry_available": job.get("retry_count", 0) < 3,
        }
    
    def _to_extraction_job(self, job_data: Dict[str, Any]) -> ExtractionJob:
        """Convert job data dict to ExtractionJob model."""
        status_value = job_data["status"].value if isinstance(job_data["status"], JobStatus) else job_data["status"]
        return ExtractionJob(
            id=job_data["id"],
            pdf_document_id=job_data["pdf_id"],
            status=status_value,
            start_time=job_data.get("started_at"),
            end_time=job_data.get("completed_at"),
            elapsed_time_ms=0,
            error=job_data.get("error"),
            llm_model="llama2",
            retry_count=job_data.get("retry_count", 0),
        )
    
    def cleanup_old_jobs(self, older_than_hours: int = 24) -> int:
        """
        Clean up old extraction jobs.
        
        Args:
            older_than_hours: Delete jobs older than this
            
        Returns:
            Number of jobs deleted
        """
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        to_delete = [
            jid for jid, job in self.jobs.items()
            if job.get("created_at", datetime.utcnow()) < cutoff
        ]
        
        for jid in to_delete:
            del self.jobs[jid]
            logger.info(f"Deleted old job {jid}")
        
        return len(to_delete)


# Global job manager instance
job_manager = JobManager()
