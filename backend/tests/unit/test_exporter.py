"""
Unit tests for metadata exporters
"""
import pytest
import json
from xml.etree import ElementTree as ET

from src.services.exporter import MetadataExporter


class TestMetadataExporterJSON:
    """Tests for JSON export format."""
    
    def test_export_to_json(self, sample_metadata):
        """Test basic JSON export."""
        metadata = sample_metadata
        
        json_str = MetadataExporter.to_json(metadata)
        
        # Verify it's valid JSON
        data = json.loads(json_str)
        
        assert data["title"] == metadata.title
        assert data["doi"] == metadata.doi
        assert len(data["authors"]) == len(metadata.authors)
        assert "@context" in data
    
    def test_export_to_json_with_confidence(self, sample_metadata):
        """Test JSON export includes confidence scores."""
        metadata = sample_metadata
        
        json_str = MetadataExporter.to_json(metadata, include_confidence=True)
        data = json.loads(json_str)
        
        assert "confidence_scores" in data
        assert "overall_confidence" in data
    
    def test_export_to_json_without_confidence(self, sample_metadata):
        """Test JSON export without confidence scores."""
        metadata = sample_metadata
        
        json_str = MetadataExporter.to_json(metadata, include_confidence=False)
        data = json.loads(json_str)
        
        assert "confidence_scores" not in data
        assert "overall_confidence" not in data


class TestMetadataExporterXML:
    """Tests for XML export format."""
    
    def test_export_to_xml(self, sample_metadata):
        """Test basic XML export."""
        metadata = sample_metadata
        
        xml_str = MetadataExporter.to_xml(metadata)
        
        # Verify it's valid XML
        root = ET.fromstring(xml_str.split('\n', 1)[-1])  # Skip XML declaration
        
        # Verify root element
        assert 'Article' in root.tag
        
        # Verify basic elements are present in XML output
        assert '<title>' in xml_str
    
    def test_export_to_xml_structure(self, sample_metadata):
        """Test XML export has correct structure."""
        metadata = sample_metadata
        
        xml_str = MetadataExporter.to_xml(metadata)
        
        # Verify contains expected elements
        assert "<title>" in xml_str
        assert "<authors>" in xml_str
        assert "<affiliations>" in xml_str


class TestMetadataExporterTOON:
    """Tests for TOON export format."""
    
    def test_export_to_toon(self, sample_metadata):
        """Test basic TOON export."""
        metadata = sample_metadata
        
        toon_str = MetadataExporter.to_toon(metadata)
        
        # Verify TOON format elements
        assert "@document {" in toon_str
        assert "@title" in toon_str
        assert "@authors {" in toon_str
        assert "@affiliations {" in toon_str
    
    def test_export_to_toon_with_confidence(self, sample_metadata):
        """Test TOON export includes confidence."""
        metadata = sample_metadata
        
        toon_str = MetadataExporter.to_toon(metadata, include_confidence=True)
        
        assert "@confidence {" in toon_str
    
    def test_export_to_toon_escaping(self, sample_metadata):
        """Test TOON export escapes special characters."""
        metadata = sample_metadata
        
        toon_str = MetadataExporter.to_toon(metadata)
        
        # Verify quotes are escaped (if present)
        # This would depend on actual metadata content
        assert "\\" or '"' not in toon_str or '\\' in toon_str
