"""
Unit tests for Pydantic models
"""
import pytest
from datetime import datetime
from src.models.metadata import (
    Author, Affiliation, ConfidenceScores, ExtractedMetadata
)
from src.models.extraction_result import (
    ExtractionJob, ExtractResponse, StatusResponse, PDFDocument
)


class TestAuthorModel:
    """Tests for Author model."""
    
    def test_valid_author(self):
        """Test creating valid author."""
        author = Author(
            id="author-001",
            name="John Doe",
            email="john@example.com",
            orcid="0000-0000-0000-0001",
            affiliation_ids=["aff-001"]
        )
        assert author.id == "author-001"
        assert author.name == "John Doe"
    
    def test_author_required_fields(self):
        """Test author requires id and name."""
        with pytest.raises(ValueError):
            Author(id="author-001")  # Missing name
    
    def test_author_invalid_orcid(self):
        """Test author with invalid ORCID format."""
        with pytest.raises(ValueError):
            Author(
                id="author-001",
                name="John Doe",
                orcid="invalid-orcid"
            )


class TestAffiliationModel:
    """Tests for Affiliation model."""
    
    def test_valid_affiliation(self):
        """Test creating valid affiliation."""
        aff = Affiliation(
            id="aff-001",
            institution="Test University",
            department="Computer Science"
        )
        assert aff.id == "aff-001"
        assert aff.institution == "Test University"
    
    def test_affiliation_required_fields(self):
        """Test affiliation requires id and institution."""
        with pytest.raises(ValueError):
            Affiliation(id="aff-001")  # Missing institution


class TestConfidenceScoresModel:
    """Tests for ConfidenceScores model."""
    
    def test_valid_confidence_scores(self):
        """Test creating valid confidence scores."""
        scores = ConfidenceScores(
            title=0.95,
            doi=0.87,
            authors=0.92
        )
        assert scores.title == 0.95
        assert scores.doi == 0.87
    
    def test_confidence_score_bounds(self):
        """Test confidence scores must be 0-1."""
        with pytest.raises(ValueError):
            ConfidenceScores(title=1.5)
        
        with pytest.raises(ValueError):
            ConfidenceScores(title=-0.1)


class TestExtractedMetadataModel:
    """Tests for ExtractedMetadata model."""
    
    def test_valid_metadata(self):
        """Test creating valid extracted metadata."""
        metadata = ExtractedMetadata(
            id="metadata-001",
            extraction_job_id="job-001",
            title="Sample Article",
            overall_confidence=0.90,
            extraction_timestamp=datetime.now()
        )
        assert metadata.id == "metadata-001"
        assert metadata.title == "Sample Article"
    
    def test_metadata_required_fields(self):
        """Test metadata requires title and overall_confidence."""
        with pytest.raises(ValueError):
            ExtractedMetadata(
                id="metadata-001",
                extraction_job_id="job-001",
                overall_confidence=0.90,
                extraction_timestamp=datetime.now()
                # Missing title
            )
    
    def test_metadata_keyword_limit(self):
        """Test metadata enforces keyword limit."""
        with pytest.raises(ValueError):
            ExtractedMetadata(
                id="metadata-001",
                extraction_job_id="job-001",
                title="Sample Article",
                keywords=["K"] * 51,  # More than 50
                overall_confidence=0.90,
                extraction_timestamp=datetime.now()
            )
    
    def test_metadata_author_limit(self):
        """Test metadata enforces author limit."""
        authors = [
            Author(id=f"author-{i:03d}", name=f"Author {i}")
            for i in range(101)
        ]
        with pytest.raises(ValueError):
            ExtractedMetadata(
                id="metadata-001",
                extraction_job_id="job-001",
                title="Sample Article",
                authors=authors,  # More than 100
                overall_confidence=0.90,
                extraction_timestamp=datetime.now()
            )


class TestExtractionJobModel:
    """Tests for ExtractionJob model."""
    
    def test_valid_extraction_job(self):
        """Test creating valid extraction job."""
        job = ExtractionJob(
            id="job-001",
            pdf_document_id="pdf-001",
            status="pending"
        )
        assert job.id == "job-001"
        assert job.status == "pending"
    
    def test_extraction_job_status_values(self):
        """Test extraction job status enum."""
        valid_statuses = ["pending", "processing", "completed", "failed", "timeout"]
        for status in valid_statuses:
            job = ExtractionJob(
                id="job-001",
                pdf_document_id="pdf-001",
                status=status
            )
            assert job.status == status


class TestExtractResponseModel:
    """Tests for ExtractResponse model."""
    
    def test_valid_extract_response(self):
        """Test creating valid extract response."""
        response = ExtractResponse(
            job_id="job-001",
            pdf_id="pdf-001"
        )
        assert response.job_id == "job-001"
        assert response.status == "pending"


class TestStatusResponseModel:
    """Tests for StatusResponse model."""
    
    def test_valid_status_response(self):
        """Test creating valid status response."""
        response = StatusResponse(
            status="processing",
            elapsed_time_ms=5000
        )
        assert response.status == "processing"
        assert response.elapsed_time_ms == 5000
    
    def test_status_response_with_metadata(self):
        """Test status response with extracted metadata."""
        metadata = ExtractedMetadata(
            id="metadata-001",
            extraction_job_id="job-001",
            title="Sample Article",
            overall_confidence=0.90,
            extraction_timestamp=datetime.now()
        )
        response = StatusResponse(
            status="completed",
            metadata=metadata
        )
        assert response.status == "completed"
        assert response.metadata is not None


class TestPDFDocumentModel:
    """Tests for PDFDocument model."""
    
    def test_valid_pdf_document(self):
        """Test creating valid PDF document."""
        doc = PDFDocument(
            id="pdf-001",
            filename="test.pdf",
            file_size=2097152,
            upload_timestamp=datetime.now(),
            storage_location="/tmp/uploads/test.pdf"
        )
        assert doc.id == "pdf-001"
        assert doc.filename == "test.pdf"
    
    def test_pdf_document_file_size_limit(self):
        """Test PDF document enforces file size limit."""
        with pytest.raises(ValueError):
            PDFDocument(
                id="pdf-001",
                filename="test.pdf",
                file_size=52428801,  # Over 50MB
                upload_timestamp=datetime.now(),
                storage_location="/tmp/uploads/test.pdf"
            )
