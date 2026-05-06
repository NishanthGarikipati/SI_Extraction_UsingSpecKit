"""
Export metadata in multiple formats: JSON, XML, TOON
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from xml.etree import ElementTree as ET
from xml.dom import minidom

from src.models.metadata import ExtractedMetadata


class ExportError(Exception):
    """Raised when export generation fails."""
    pass


class MetadataExporter:
    """Exports extracted metadata in various formats."""
    
    @staticmethod
    def to_json(
        metadata: ExtractedMetadata,
        include_confidence: bool = True,
        pretty: bool = True
    ) -> str:
        """
        Export metadata as JSON.
        
        Args:
            metadata: ExtractedMetadata object
            include_confidence: Include confidence scores in output
            pretty: Pretty-print JSON
            
        Returns:
            JSON string
        """
        data = {
            "@context": "https://schema.org/ScholarlyArticle",
            "id": metadata.id,
            "title": metadata.title,
            "doi": metadata.doi,
            "abstract": metadata.abstract,
            "keywords": metadata.keywords,
            "publication_date": metadata.publication_date,
            "journal": metadata.journal,
            "authors": [
                {
                    "id": author.id,
                    "name": author.name,
                    "email": author.email,
                    "orcid": author.orcid,
                    "affiliation_ids": author.affiliation_ids,
                }
                for author in metadata.authors
            ],
            "affiliations": [
                {
                    "id": aff.id,
                    "institution": aff.institution,
                    "department": aff.department,
                    "city": aff.city,
                    "country": aff.country,
                    "postal_code": aff.postal_code,
                }
                for aff in metadata.affiliations
            ],
            "extraction_timestamp": metadata.extraction_timestamp.isoformat(),
            "source_file": metadata.source_file,
        }
        
        if include_confidence:
            data["confidence_scores"] = {
                "title": metadata.confidence_scores.title,
                "doi": metadata.confidence_scores.doi,
                "authors": metadata.confidence_scores.authors,
                "abstract": metadata.confidence_scores.abstract,
                "keywords": metadata.confidence_scores.keywords,
                "publication_date": metadata.confidence_scores.publication_date,
                "journal": metadata.confidence_scores.journal,
                "affiliations": metadata.confidence_scores.affiliations,
            }
            data["overall_confidence"] = metadata.overall_confidence
        
        if pretty:
            return json.dumps(data, indent=2, default=str)
        else:
            return json.dumps(data, default=str)
    
    @staticmethod
    def to_xml(
        metadata: ExtractedMetadata,
        include_confidence: bool = True,
        pretty: bool = True
    ) -> str:
        """
        Export metadata as XML.
        
        Args:
            metadata: ExtractedMetadata object
            include_confidence: Include confidence scores in output
            pretty: Pretty-print XML
            
        Returns:
            XML string
        """
        root = ET.Element("ScholarlyArticle")
        root.set("xmlns", "https://schema.org")
        root.set("id", metadata.id)
        
        # Basic fields
        ET.SubElement(root, "title").text = metadata.title
        
        if metadata.doi:
            ET.SubElement(root, "doi").text = metadata.doi
        
        if metadata.abstract:
            ET.SubElement(root, "abstract").text = metadata.abstract
        
        if metadata.publication_date:
            ET.SubElement(root, "publication_date").text = metadata.publication_date
        
        if metadata.journal:
            ET.SubElement(root, "journal").text = metadata.journal
        
        # Keywords
        if metadata.keywords:
            keywords_elem = ET.SubElement(root, "keywords")
            for keyword in metadata.keywords:
                ET.SubElement(keywords_elem, "keyword").text = keyword
        
        # Authors
        if metadata.authors:
            authors_elem = ET.SubElement(root, "authors")
            for author in metadata.authors:
                author_elem = ET.SubElement(authors_elem, "author")
                author_elem.set("id", author.id)
                ET.SubElement(author_elem, "name").text = author.name
                if author.email:
                    ET.SubElement(author_elem, "email").text = author.email
                if author.orcid:
                    ET.SubElement(author_elem, "orcid").text = author.orcid
                if author.affiliation_ids:
                    for aff_id in author.affiliation_ids:
                        ET.SubElement(author_elem, "affiliation_id").text = aff_id
        
        # Affiliations
        if metadata.affiliations:
            affiliations_elem = ET.SubElement(root, "affiliations")
            for aff in metadata.affiliations:
                aff_elem = ET.SubElement(affiliations_elem, "affiliation")
                aff_elem.set("id", aff.id)
                ET.SubElement(aff_elem, "institution").text = aff.institution
                if aff.department:
                    ET.SubElement(aff_elem, "department").text = aff.department
                if aff.city:
                    ET.SubElement(aff_elem, "city").text = aff.city
                if aff.country:
                    ET.SubElement(aff_elem, "country").text = aff.country
                if aff.postal_code:
                    ET.SubElement(aff_elem, "postal_code").text = aff.postal_code
        
        # Metadata
        metadata_elem = ET.SubElement(root, "metadata")
        ET.SubElement(metadata_elem, "extraction_timestamp").text = metadata.extraction_timestamp.isoformat()
        if metadata.source_file:
            ET.SubElement(metadata_elem, "source_file").text = metadata.source_file
        
        # Confidence scores
        if include_confidence:
            confidence_elem = ET.SubElement(root, "confidence_scores")
            if metadata.confidence_scores.title is not None:
                ET.SubElement(confidence_elem, "title").text = str(metadata.confidence_scores.title)
            if metadata.confidence_scores.doi is not None:
                ET.SubElement(confidence_elem, "doi").text = str(metadata.confidence_scores.doi)
            if metadata.confidence_scores.authors is not None:
                ET.SubElement(confidence_elem, "authors").text = str(metadata.confidence_scores.authors)
            ET.SubElement(root, "overall_confidence").text = str(metadata.overall_confidence)
        
        xml_str = ET.tostring(root, encoding='unicode')
        
        if pretty:
            dom = minidom.parseString(xml_str)
            return dom.toprettyxml(indent="  ")
        else:
            return xml_str
    
    @staticmethod
    def to_toon(
        metadata: ExtractedMetadata,
        include_confidence: bool = True
    ) -> str:
        """
        Export metadata as TOON (Token-Oriented Object Notation).
        Custom format with @name {} syntax.
        
        Args:
            metadata: ExtractedMetadata object
            include_confidence: Include confidence scores in output
            
        Returns:
            TOON string
        """
        lines = []
        
        # Header
        lines.append("@document {")
        lines.append(f'  @id "{metadata.id}"')
        lines.append(f'  @title "{MetadataExporter._escape_toon(metadata.title)}"')
        
        # Basic fields
        if metadata.doi:
            lines.append(f'  @doi "{MetadataExporter._escape_toon(metadata.doi)}"')
        
        if metadata.journal:
            lines.append(f'  @journal "{MetadataExporter._escape_toon(metadata.journal)}"')
        
        if metadata.publication_date:
            lines.append(f'  @publication_date "{metadata.publication_date}"')
        
        # Abstract
        if metadata.abstract:
            abstract_lines = metadata.abstract.split('\n')
            lines.append("  @abstract {")
            for line in abstract_lines:
                escaped = MetadataExporter._escape_toon(line)
                lines.append(f'    "{escaped}"')
            lines.append("  }")
        
        # Keywords
        if metadata.keywords:
            lines.append("  @keywords {")
            for keyword in metadata.keywords:
                lines.append(f'    "{MetadataExporter._escape_toon(keyword)}"')
            lines.append("  }")
        
        # Authors
        if metadata.authors:
            lines.append("  @authors {")
            for author in metadata.authors:
                author_header = f"    @author {{id: {author.id}}} {{"
                lines.append(author_header)
                lines.append(f'      name "{MetadataExporter._escape_toon(author.name)}"')
                if author.email:
                    lines.append(f'      email "{author.email}"')
                if author.orcid:
                    lines.append(f'      orcid "{author.orcid}"')
                lines.append("    }")
            lines.append("  }")
        
        # Affiliations
        if metadata.affiliations:
            lines.append("  @affiliations {")
            for aff in metadata.affiliations:
                aff_header = f"    @affiliation {{id: {aff.id}}} {{"
                lines.append(aff_header)
                lines.append(f'      institution "{MetadataExporter._escape_toon(aff.institution)}"')
                if aff.department:
                    lines.append(f'      department "{MetadataExporter._escape_toon(aff.department)}"')
                if aff.city:
                    lines.append(f'      city "{MetadataExporter._escape_toon(aff.city)}"')
                if aff.country:
                    lines.append(f'      country "{MetadataExporter._escape_toon(aff.country)}"')
                lines.append("    }")
            lines.append("  }")
        
        # Confidence scores
        if include_confidence:
            lines.append("  @confidence {")
            if metadata.confidence_scores.title is not None:
                lines.append(f"    title: {metadata.confidence_scores.title}")
            if metadata.confidence_scores.doi is not None:
                lines.append(f"    doi: {metadata.confidence_scores.doi}")
            lines.append(f"    overall: {metadata.overall_confidence}")
            lines.append("  }")
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def _escape_toon(text: Optional[str]) -> str:
        """Escape special characters for TOON format."""
        if not text:
            return ""
        return text.replace('"', '\\"').replace('\n', ' ')
