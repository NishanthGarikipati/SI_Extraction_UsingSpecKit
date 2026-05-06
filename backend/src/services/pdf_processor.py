"""
PDF processing utilities for extraction, validation, and text extraction
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import pdfplumber
from PyPDF2 import PdfReader
import logging


logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Base exception for PDF processing errors."""
    pass


class PDFValidationError(PDFProcessingError):
    """Raised when PDF validation fails."""
    pass


class TextExtractionError(PDFProcessingError):
    """Raised when text extraction fails."""
    pass


class PDFProcessor:
    """Handles PDF validation and text extraction."""
    
    MAX_FILE_SIZE = 52428800  # 50MB in bytes
    SUPPORTED_FORMATS = {'.pdf'}
    
    @staticmethod
    def validate_file(file_path: str | Path, file_size: int) -> None:
        """
        Validate PDF file before processing.
        
        Args:
            file_path: Path to PDF file
            file_size: File size in bytes
            
        Raises:
            PDFValidationError: If validation fails
        """
        file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            raise PDFValidationError(f"File not found: {file_path}")
        
        # Check file extension
        if file_path.suffix.lower() not in PDFProcessor.SUPPORTED_FORMATS:
            raise PDFValidationError(
                f"Unsupported file format: {file_path.suffix}. Expected: .pdf"
            )
        
        # Check file size
        if file_size > PDFProcessor.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            max_mb = PDFProcessor.MAX_FILE_SIZE / (1024 * 1024)
            raise PDFValidationError(
                f"File size {size_mb:.1f}MB exceeds maximum {max_mb:.1f}MB"
            )
        
        # Check if valid PDF
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    raise PDFValidationError("File is not a valid PDF (invalid header)")
        except Exception as e:
            raise PDFValidationError(f"Failed to validate PDF: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str | Path) -> Tuple[str, int]:
        """
        Extract text content from PDF using pdfplumber.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
            
        Raises:
            TextExtractionError: If extraction fails
        """
        file_path = Path(file_path)
        
        try:
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                text_content = ""
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
                
                if not text_content.strip():
                    raise TextExtractionError("No text content found in PDF")
                
                logger.info(f"Extracted text from {page_count} pages, {len(text_content)} characters")
                return text_content, page_count
                
        except pdfplumber.PDFException as e:
            raise TextExtractionError(f"pdfplumber extraction failed: {str(e)}")
        except Exception as e:
            raise TextExtractionError(f"Text extraction failed: {str(e)}")
    
    @staticmethod
    def extract_metadata(file_path: str | Path) -> dict:
        """
        Extract PDF metadata (title, author, subject, etc.) using PyPDF2.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary of PDF metadata
        """
        file_path = Path(file_path)
        metadata = {}
        
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                    }
                
                logger.info(f"Extracted PDF metadata: {metadata}")
                
        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {str(e)}")
        
        return metadata
    
    @staticmethod
    def process_pdf(file_path: str | Path, file_size: int) -> dict:
        """
        Complete PDF processing pipeline: validate, extract text and metadata.
        
        Args:
            file_path: Path to PDF file
            file_size: File size in bytes
            
        Returns:
            Dictionary with extraction results
            
        Raises:
            PDFProcessingError: If any processing step fails
        """
        file_path = Path(file_path)
        
        # Validate
        PDFProcessor.validate_file(file_path, file_size)
        logger.info(f"PDF validation passed: {file_path}")
        
        # Extract text
        text_content, page_count = PDFProcessor.extract_text(file_path)
        logger.info(f"Text extraction completed: {page_count} pages")
        
        # Extract metadata
        pdf_metadata = PDFProcessor.extract_metadata(file_path)
        
        return {
            'text_content': text_content,
            'page_count': page_count,
            'pdf_metadata': pdf_metadata,
            'file_size': file_size,
            'filename': file_path.name,
        }
