"""
Integration tests for extraction endpoint
"""
import pytest
import asyncio
from datetime import datetime

from src.services.rag_extractor import RAGExtractor, MetadataExtractionError, OllamaConnectionError
from src.services.job_manager import JobManager, job_manager
from src.models.metadata import ExtractedMetadata


@pytest.mark.asyncio
async def test_extraction_job_lifecycle():
    """Test complete extraction job lifecycle."""
    # Create job
    job_id = "test-job-001"
    pdf_id = "test-pdf-001"
    temp_path = "/tmp/test.pdf"
    filename = "test.pdf"
    
    job = job_manager.create_job(job_id, pdf_id, temp_path, filename)
    
    assert job.id == job_id
    assert job.pdf_document_id == pdf_id
    assert job.status == "pending"
    
    # Get status
    status = job_manager.get_status(job_id)
    assert status["status"] == "pending"
    assert status["job_id"] == job_id


@pytest.mark.asyncio
async def test_rag_extractor_metadata_parsing():
    """Test RAG extractor metadata parsing."""
    extractor = RAGExtractor()
    
    # Test mock response parsing
    llm_output = """
{
    "title": "Test Article",
    "doi": "10.1234/test.5678",
    "abstract": "This is a test abstract.",
    "keywords": ["test", "extraction"],
    "publication_date": "2024-01-01",
    "journal": "Test Journal",
    "authors": [
        {"name": "John Doe", "email": "john@example.com"}
    ],
    "affiliations": [
        {"institution": "Test University", "country": "USA"}
    ],
    "confidence_scores": {
        "title": 0.95,
        "doi": 0.87,
        "authors": 0.91
    }
}
    """
    
    job_id = "test-job-001"
    metadata = extractor._parse_extraction_response(llm_output, job_id)
    
    assert isinstance(metadata, ExtractedMetadata)
    assert metadata.title == "Test Article"
    assert metadata.doi == "10.1234/test.5678"
    assert len(metadata.authors) == 1
    assert len(metadata.affiliations) == 1
    assert metadata.confidence_scores.title == 0.95


@pytest.mark.asyncio
async def test_rag_extractor_invalid_json():
    """Test RAG extractor with invalid JSON."""
    extractor = RAGExtractor()
    
    llm_output = "This is not valid JSON"
    job_id = "test-job-001"
    
    with pytest.raises(MetadataExtractionError):
        extractor._parse_extraction_response(llm_output, job_id)


@pytest.mark.asyncio
async def test_rag_extractor_fallback_on_ollama_unavailable():
    """Test fallback extraction when Ollama is unavailable."""
    extractor = RAGExtractor()

    async def failing_call(prompt: str) -> str:
        raise OllamaConnectionError("Failed to connect to Ollama")

    extractor._call_ollama = failing_call
    text_content = (
        "Test Article\n"
        "John Doe, Jane Smith\n"
        "Abstract: This is a sample abstract.\n\n"
        "Keywords: AI, metadata, extraction\n"
        "DOI: 10.1234/test.5678\n"
        "Journal of Testing\n"
    )

    metadata = await extractor.extract_metadata_async(text_content, "test-job-002")

    assert metadata.title == "Test Article"
    assert metadata.doi == "10.1234/test.5678"
    assert metadata.abstract is not None
    assert metadata.keywords == ["AI", "metadata", "extraction"]
    assert len(metadata.authors) >= 1


@pytest.mark.asyncio
async def test_job_manager_cleanup():
    """Test job manager cleanup of old jobs."""
    mgr = JobManager()
    
    # Create jobs
    mgr.create_job("job-1", "pdf-1", "/tmp/test1.pdf", "test1.pdf")
    mgr.create_job("job-2", "pdf-2", "/tmp/test2.pdf", "test2.pdf")
    
    assert len(mgr.jobs) == 2
    
    # Cleanup should not delete recent jobs
    deleted = mgr.cleanup_old_jobs(older_than_hours=24)
    assert deleted == 0
    assert len(mgr.jobs) == 2
