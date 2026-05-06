import pytest
from typing import Generator
import json
from pathlib import Path

from src.models.metadata import ExtractedMetadata


@pytest.fixture
def mock_pdf_sample() -> bytes:
    """Create a minimal valid PDF for testing."""
    # Minimal PDF structure for testing
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Sample PDF) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000333 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
426
%%EOF
"""
    return pdf_content


@pytest.fixture
def sample_extraction_job() -> dict:
    """Sample extraction job data for testing."""
    return {
        "id": "job-12345",
        "pdf_document_id": "pdf-001",
        "status": "pending",
        "start_time": "2026-05-04T10:00:00Z",
        "end_time": None,
        "elapsed_time_ms": 0,
        "error": None,
        "llm_model": "llama2",
        "retry_count": 0,
        "raw_llm_output": None
    }


@pytest.fixture
def sample_metadata() -> ExtractedMetadata:
    """Sample extracted metadata for testing."""
    return ExtractedMetadata(
        id="metadata-001",
        extraction_job_id="job-12345",
        title="Sample Article Title",
        doi="10.1234/example.5678",
        abstract="This is a sample abstract...",
        keywords=["keyword1", "keyword2", "keyword3"],
        authors=[
            {
                "id": "author-001",
                "name": "John Doe",
                "email": "john@example.com",
                "orcid": "0000-0000-0000-0001",
                "affiliation_ids": ["aff-001"]
            }
        ],
        affiliations=[
            {
                "id": "aff-001",
                "institution": "Test University",
                "department": "Computer Science",
                "city": "Cambridge",
                "country": "USA",
                "postal_code": "02138"
            }
        ],
        publication_date="2026-05-01",
        journal="Sample Journal",
        confidence_scores={
            "title": 0.95,
            "doi": 0.87,
            "authors": 0.92,
            "abstract": 0.88
        },
        overall_confidence=0.90,
        extraction_timestamp="2026-05-04T10:00:30Z"
    )


@pytest.fixture
def temp_pdf_file(mock_pdf_sample, tmp_path) -> Path:
    """Create a temporary PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(mock_pdf_sample)
    return pdf_path
