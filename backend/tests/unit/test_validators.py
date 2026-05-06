"""
Unit tests for PDF validators
"""
import pytest
from src.utils.validators import (
    PDFValidator, MetadataValidator, ConfidenceValidator,
    validate_metadata_fields, ValidationError
)


class TestPDFValidator:
    """Tests for PDF file validation."""
    
    def test_validate_file_size_valid(self):
        """Test valid file sizes are accepted."""
        assert PDFValidator.validate_file_size(1000) is True
        assert PDFValidator.validate_file_size(52428800) is True  # Exactly 50MB
        assert PDFValidator.validate_file_size(1) is True
    
    def test_validate_file_size_invalid(self):
        """Test invalid file sizes are rejected."""
        assert PDFValidator.validate_file_size(0) is False
        assert PDFValidator.validate_file_size(-1) is False
        assert PDFValidator.validate_file_size(52428801) is False  # Over 50MB
    
    def test_validate_filename_valid(self):
        """Test valid PDF filenames."""
        assert PDFValidator.validate_filename("document.pdf") is True
        assert PDFValidator.validate_filename("test.PDF") is True
        assert PDFValidator.validate_filename("paper_2026.pdf") is True
    
    def test_validate_filename_invalid(self):
        """Test invalid filenames are rejected."""
        assert PDFValidator.validate_filename("") is False
        assert PDFValidator.validate_filename("document.txt") is False
        assert PDFValidator.validate_filename("document") is False
    
    def test_size_error_message(self):
        """Test error messages for invalid sizes."""
        assert PDFValidator.get_size_error_message(0) is not None
        assert PDFValidator.get_size_error_message(-1) is not None
        assert PDFValidator.get_size_error_message(100 * 1024 * 1024) is not None
        assert PDFValidator.get_size_error_message(1000) is None


class TestMetadataValidator:
    """Tests for metadata field validation."""
    
    def test_validate_doi(self):
        """Test DOI validation."""
        assert MetadataValidator.validate_doi("10.1234/example.5678") is True
        assert MetadataValidator.validate_doi(None) is True
        assert MetadataValidator.validate_doi("") is True
        assert MetadataValidator.validate_doi("not-a-doi") is False
        assert MetadataValidator.validate_doi("10.invalid") is False
    
    def test_validate_orcid(self):
        """Test ORCID validation."""
        assert MetadataValidator.validate_orcid("0000-0000-0000-0001") is True
        assert MetadataValidator.validate_orcid("1234-5678-9012-345X") is True
        assert MetadataValidator.validate_orcid(None) is True
        assert MetadataValidator.validate_orcid("") is True
        assert MetadataValidator.validate_orcid("0000-0000-0000-000") is False  # Too short
    
    def test_validate_email(self):
        """Test email validation."""
        assert MetadataValidator.validate_email("test@example.com") is True
        assert MetadataValidator.validate_email("user.name@domain.co.uk") is True
        assert MetadataValidator.validate_email(None) is True
        assert MetadataValidator.validate_email("") is True
        assert MetadataValidator.validate_email("not-an-email") is False
    
    def test_validate_title(self):
        """Test title validation."""
        assert MetadataValidator.validate_title("Sample Title") is True
        assert MetadataValidator.validate_title("A" * 500) is True
        assert MetadataValidator.validate_title(None) is False
        assert MetadataValidator.validate_title("") is False
        assert MetadataValidator.validate_title("A" * 501) is False
    
    def test_validate_abstract(self):
        """Test abstract validation."""
        assert MetadataValidator.validate_abstract("Sample abstract") is True
        assert MetadataValidator.validate_abstract(None) is True
        assert MetadataValidator.validate_abstract("") is True
        assert MetadataValidator.validate_abstract("A" * 5000) is True
        assert MetadataValidator.validate_abstract("A" * 5001) is False
    
    def test_validate_keywords(self):
        """Test keywords validation."""
        assert MetadataValidator.validate_keywords(["keyword1", "keyword2"]) is True
        assert MetadataValidator.validate_keywords([]) is True
        assert MetadataValidator.validate_keywords(None) is True
        assert MetadataValidator.validate_keywords(["K"] * 50) is True
        assert MetadataValidator.validate_keywords(["K"] * 51) is False
        assert MetadataValidator.validate_keywords("not-a-list") is False
    
    def test_validate_confidence_score(self):
        """Test confidence score validation."""
        assert MetadataValidator.validate_confidence_score(0.0) is True
        assert MetadataValidator.validate_confidence_score(0.5) is True
        assert MetadataValidator.validate_confidence_score(1.0) is True
        assert MetadataValidator.validate_confidence_score(None) is True
        assert MetadataValidator.validate_confidence_score(-0.1) is False
        assert MetadataValidator.validate_confidence_score(1.1) is False


class TestConfidenceValidator:
    """Tests for confidence score validation."""
    
    def test_validate_score(self):
        """Test individual score validation."""
        assert ConfidenceValidator.validate_score(0.0) is True
        assert ConfidenceValidator.validate_score(0.75) is True
        assert ConfidenceValidator.validate_score(1.0) is True
        assert ConfidenceValidator.validate_score(-0.1) is False
        assert ConfidenceValidator.validate_score(1.1) is False
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation."""
        scores = {"title": 0.95, "authors": 0.90, "doi": 0.85}
        result = ConfidenceValidator.calculate_overall_confidence(scores)
        assert result == pytest.approx(0.9, abs=0.01)
        
        # Test with empty scores
        assert ConfidenceValidator.calculate_overall_confidence({}) == 0.0
        assert ConfidenceValidator.calculate_overall_confidence(None) == 0.0


class TestValidateMetadataFields:
    """Tests for complete metadata validation."""
    
    def test_valid_metadata(self):
        """Test validation of valid metadata."""
        metadata = {
            "title": "Sample Article",
            "doi": "10.1234/example.5678",
            "keywords": ["keyword1", "keyword2"],
        }
        errors = validate_metadata_fields(metadata)
        assert len(errors) == 0
    
    def test_missing_title(self):
        """Test validation fails without title."""
        metadata = {"doi": "10.1234/example.5678"}
        errors = validate_metadata_fields(metadata)
        assert len(errors) > 0
        assert any("Title" in error for error in errors)
    
    def test_invalid_doi(self):
        """Test validation fails with invalid DOI."""
        metadata = {
            "title": "Sample Article",
            "doi": "not-a-doi",
        }
        errors = validate_metadata_fields(metadata)
        assert any("DOI" in error for error in errors)
    
    def test_too_many_keywords(self):
        """Test validation fails with too many keywords."""
        metadata = {
            "title": "Sample Article",
            "keywords": ["K"] * 51,
        }
        errors = validate_metadata_fields(metadata)
        assert any("Keywords" in error for error in errors)
