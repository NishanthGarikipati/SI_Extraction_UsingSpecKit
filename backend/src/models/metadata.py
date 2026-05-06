"""
Pydantic models for extracted metadata following contracts/metadata-schema.json
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class Author(BaseModel):
    """Author model with name, email, ORCID, and affiliations."""
    id: str = Field(..., description="Unique author ID")
    name: str = Field(..., min_length=1, max_length=200, description="Author full name")
    email: Optional[str] = Field(None, description="Author email address")
    orcid: Optional[str] = Field(None, pattern=r"^\d{4}-\d{4}-\d{4}-\d{3}[0-9X]$", description="ORCID identifier")
    affiliation_ids: List[str] = Field(default_factory=list, description="List of affiliation IDs")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "author-001",
                "name": "John Doe",
                "email": "john@example.com",
                "orcid": "0000-0000-0000-0001",
                "affiliation_ids": ["aff-001"]
            }
        }


class Affiliation(BaseModel):
    """Affiliation model for author institutions and departments."""
    id: str = Field(..., description="Unique affiliation ID")
    institution: str = Field(..., min_length=1, max_length=300, description="Institution name")
    department: Optional[str] = Field(None, max_length=200, description="Department or faculty")
    city: Optional[str] = Field(None, max_length=100, description="City")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "aff-001",
                "institution": "Test University",
                "department": "Computer Science",
                "city": "Cambridge",
                "country": "USA",
                "postal_code": "02138"
            }
        }


class ConfidenceScores(BaseModel):
    """Confidence scores for each extracted metadata field."""
    title: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in title extraction")
    doi: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in DOI extraction")
    authors: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in authors extraction")
    abstract: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in abstract extraction")
    keywords: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in keywords extraction")
    publication_date: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in publication date")
    journal: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in journal extraction")
    affiliations: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in affiliations extraction")

    class Config:
        json_schema_extra = {
            "example": {
                "title": 0.95,
                "doi": 0.87,
                "authors": 0.92,
                "abstract": 0.88
            }
        }


class ExtractedMetadata(BaseModel):
    """Complete extracted metadata from a PDF document."""
    id: str = Field(..., description="Unique metadata ID")
    extraction_job_id: str = Field(..., description="Associated extraction job ID")
    
    # Core metadata fields
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    doi: Optional[str] = Field(None, pattern=r"^10\.\d+/.+$", description="Digital Object Identifier")
    abstract: Optional[str] = Field(None, max_length=5000, description="Article abstract")
    keywords: List[str] = Field(default_factory=list, max_length=50, description="Keywords/tags")
    publication_date: Optional[str] = Field(None, description="Publication date (ISO 8601)")
    journal: Optional[str] = Field(None, max_length=300, description="Journal or publication name")
    
    # Author and affiliation information
    authors: List[Author] = Field(default_factory=list, max_length=100, description="List of authors")
    affiliations: List[Affiliation] = Field(default_factory=list, description="List of affiliations")
    
    # Confidence and extraction metadata
    confidence_scores: ConfidenceScores = Field(default_factory=ConfidenceScores, description="Per-field confidence scores")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall extraction confidence (0.0-1.0)")
    extraction_timestamp: datetime = Field(..., description="When metadata was extracted")
    source_file: Optional[str] = Field(None, description="Source PDF filename")

    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        if len(v) > 50:
            raise ValueError('Maximum 50 keywords allowed')
        return v

    @field_validator('authors')
    @classmethod
    def validate_authors(cls, v):
        if len(v) > 100:
            raise ValueError('Maximum 100 authors allowed')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "metadata-001",
                "extraction_job_id": "job-12345",
                "title": "Sample Article Title",
                "doi": "10.1234/example.5678",
                "abstract": "This is a sample abstract...",
                "keywords": ["keyword1", "keyword2", "keyword3"],
                "authors": [
                    {
                        "id": "author-001",
                        "name": "John Doe",
                        "email": "john@example.com",
                        "orcid": "0000-0000-0000-0001",
                        "affiliation_ids": ["aff-001"]
                    }
                ],
                "affiliations": [
                    {
                        "id": "aff-001",
                        "institution": "Test University",
                        "department": "Computer Science",
                        "city": "Cambridge",
                        "country": "USA",
                        "postal_code": "02138"
                    }
                ],
                "confidence_scores": {
                    "title": 0.95,
                    "doi": 0.87,
                    "authors": 0.92,
                    "abstract": 0.88
                },
                "overall_confidence": 0.90,
                "extraction_timestamp": "2026-05-04T10:00:30Z",
                "source_file": "example.pdf"
            }
        }
