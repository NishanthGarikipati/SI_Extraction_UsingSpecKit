"""
Validation utilities for PDFs, metadata, and API inputs
"""
import re
from typing import Optional, List
import logging


logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class PDFValidator:
    """PDF file validation utilities."""
    
    MAX_SIZE_MB = 50
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024
    
    @staticmethod
    def validate_file_size(size_bytes: int) -> bool:
        """Check if file size is within limits."""
        return 0 < size_bytes <= PDFValidator.MAX_SIZE_BYTES
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Check if filename is valid for a PDF."""
        if not filename:
            return False
        return filename.lower().endswith('.pdf')
    
    @staticmethod
    def get_size_error_message(size_bytes: int) -> Optional[str]:
        """Get error message for invalid file size."""
        if size_bytes <= 0:
            return "File size must be greater than 0 bytes"
        if size_bytes > PDFValidator.MAX_SIZE_BYTES:
            size_mb = size_bytes / (1024 * 1024)
            return f"File size {size_mb:.1f}MB exceeds maximum {PDFValidator.MAX_SIZE_MB}MB"
        return None


class MetadataValidator:
    """Metadata field validation utilities."""
    
    DOI_PATTERN = re.compile(r'^10\.\d+/\S+$')
    ORCID_PATTERN = re.compile(r'^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$')
    EMAIL_PATTERN = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    ISO8601_PATTERN = re.compile(
        r'^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:Z|[+-]\d{2}:\d{2})?)?$'
    )
    
    @staticmethod
    def validate_doi(doi: Optional[str]) -> bool:
        """Validate DOI format."""
        if not doi:
            return True
        return bool(MetadataValidator.DOI_PATTERN.match(doi))
    
    @staticmethod
    def validate_orcid(orcid: Optional[str]) -> bool:
        """Validate ORCID format."""
        if not orcid:
            return True
        return bool(MetadataValidator.ORCID_PATTERN.match(orcid))
    
    @staticmethod
    def validate_email(email: Optional[str]) -> bool:
        """Validate email format."""
        if not email:
            return True
        return bool(MetadataValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_title(title: Optional[str]) -> bool:
        """Validate title field."""
        if not title:
            return False
        return 1 <= len(title) <= 500
    
    @staticmethod
    def validate_abstract(abstract: Optional[str]) -> bool:
        """Validate abstract field."""
        if not abstract:
            return True
        return len(abstract) <= 5000
    
    @staticmethod
    def validate_keywords(keywords: Optional[List[str]]) -> bool:
        """Validate keywords list."""
        if not keywords:
            return True
        if not isinstance(keywords, list):
            return False
        if len(keywords) > 50:
            return False
        return all(isinstance(k, str) and 1 <= len(k) <= 100 for k in keywords)
    
    @staticmethod
    def validate_confidence_score(score: Optional[float]) -> bool:
        """Validate confidence score is between 0 and 1."""
        if score is None:
            return True
        return isinstance(score, (int, float)) and 0.0 <= score <= 1.0
    
    @staticmethod
    def validate_publication_date(date_str: Optional[str]) -> bool:
        """Validate ISO 8601 date format."""
        if not date_str:
            return True
        return bool(MetadataValidator.ISO8601_PATTERN.match(date_str))
    
    @staticmethod
    def validate_author_count(authors: Optional[List]) -> bool:
        """Validate number of authors."""
        if not authors:
            return True
        return len(authors) <= 100


class ConfidenceValidator:
    """Validation for confidence scores."""
    
    @staticmethod
    def validate_score(score: float) -> bool:
        """Check if score is valid confidence value."""
        return isinstance(score, (int, float)) and 0.0 <= score <= 1.0
    
    @staticmethod
    def calculate_overall_confidence(scores: dict) -> float:
        """Calculate overall confidence from individual scores."""
        if not scores:
            return 0.0
        
        valid_scores = [s for s in scores.values() if isinstance(s, (int, float))]
        if not valid_scores:
            return 0.0
        
        return sum(valid_scores) / len(valid_scores)


def validate_metadata_fields(metadata: dict) -> List[str]:
    """
    Validate all metadata fields and return list of validation errors.
    
    Args:
        metadata: Dictionary of metadata fields
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Required field validation
    if not MetadataValidator.validate_title(metadata.get('title')):
        errors.append("Title is required and must be 1-500 characters")
    
    # Optional field validation
    if not MetadataValidator.validate_doi(metadata.get('doi')):
        errors.append("Invalid DOI format")
    
    if not MetadataValidator.validate_orcid(metadata.get('orcid')):
        errors.append("Invalid ORCID format")
    
    if not MetadataValidator.validate_email(metadata.get('email')):
        errors.append("Invalid email format")
    
    if not MetadataValidator.validate_abstract(metadata.get('abstract')):
        errors.append("Abstract must be 0-5000 characters")
    
    if not MetadataValidator.validate_keywords(metadata.get('keywords')):
        errors.append("Keywords must be list of 0-50 items")
    
    if not MetadataValidator.validate_author_count(metadata.get('authors')):
        errors.append("Too many authors (max 100)")
    
    if not MetadataValidator.validate_publication_date(metadata.get('publication_date')):
        errors.append("Publication date must be ISO 8601 format")
    
    return errors
