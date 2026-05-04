# Export Formats Specification

**Phase**: 1 (Design & Contracts)  
**Date**: 2026-05-04  
**Status**: Complete

---

## Overview

This document specifies the exact format and structure for the three export file types: JSON, XML, and TOON. All formats contain identical data, just with different serialization approaches.

---

## 1. JSON Export Format

### File Extension: `.json`
### MIME Type: `application/json`

### Complete Example

```json
{
  "@context": "https://schema.org/ScholarlyArticle",
  "metadata": {
    "extraction": {
      "timestamp": "2026-05-04T14:31:00Z",
      "source_file": "paper_2024.pdf",
      "extraction_engine": "llama2-7b-ollama",
      "version": "1.0.0"
    },
    "confidence_scores": {
      "title": 0.98,
      "doi": 0.95,
      "authors": 0.92,
      "affiliations": 0.85,
      "abstract": 0.89,
      "keywords": 0.87,
      "publication_date": 0.93,
      "journal_name": 0.88
    },
    "overall_confidence": 0.91
  },
  "document": {
    "id": "meta_550e8400_e29b_41d4_a716_446655440002",
    "title": "Deep Learning for Scientific Document Analysis",
    "doi": "10.1145/3123456.3456789",
    "abstract": "This paper presents a novel approach to extracting structured metadata from scientific documents using deep learning techniques. We propose a multi-modal system that combines optical character recognition with natural language processing...",
    "keywords": [
      "deep learning",
      "document analysis",
      "metadata extraction",
      "information retrieval",
      "machine learning"
    ],
    "publication_date": "2024-01-15",
    "journal": {
      "name": "ACM Computing Surveys",
      "volume": "57",
      "issue": "2",
      "pages": {
        "start": "123",
        "end": "156"
      }
    },
    "authors": [
      {
        "id": "auth_001",
        "sequence": 1,
        "name": "Jane Smith",
        "email": "jane.smith@mit.edu",
        "orcid": "0000-0001-2345-6789",
        "affiliations": [
          {
            "id": "aff_001",
            "institution": "Massachusetts Institute of Technology",
            "department": "Computer Science and Artificial Intelligence Laboratory",
            "address": {
              "city": "Cambridge",
              "state": "MA",
              "country": "USA",
              "postal_code": "02139"
            }
          }
        ]
      },
      {
        "id": "auth_002",
        "sequence": 2,
        "name": "John Doe",
        "email": "john.doe@stanford.edu",
        "affiliations": [
          {
            "id": "aff_002",
            "institution": "Stanford University",
            "department": "Department of Computer Science",
            "address": {
              "city": "Stanford",
              "state": "CA",
              "country": "USA",
              "postal_code": "94305"
            }
          },
          {
            "id": "aff_001",
            "institution": "Massachusetts Institute of Technology",
            "department": "Computer Science and Artificial Intelligence Laboratory"
          }
        ]
      }
    ]
  }
}
```

### JSON Schema Validation

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["document"],
  "properties": {
    "@context": {
      "type": "string",
      "description": "Schema.org context URL"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "extraction": {
          "type": "object",
          "required": ["timestamp", "source_file"],
          "properties": {
            "timestamp": { "type": "string", "format": "date-time" },
            "source_file": { "type": "string" },
            "extraction_engine": { "type": "string" },
            "version": { "type": "string" }
          }
        },
        "confidence_scores": {
          "type": "object",
          "additionalProperties": { "type": "number", "minimum": 0, "maximum": 1 }
        },
        "overall_confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      }
    },
    "document": {
      "type": "object",
      "required": ["title"],
      "properties": {
        "id": { "type": "string" },
        "title": { "type": "string", "maxLength": 500 },
        "doi": { "type": "string", "pattern": "^10\\.\\d+/.+" },
        "abstract": { "type": "string", "maxLength": 5000 },
        "keywords": { "type": "array", "items": { "type": "string" } },
        "publication_date": { "type": "string", "format": "date" },
        "journal": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "volume": { "type": "string" },
            "issue": { "type": "string" },
            "pages": {
              "type": "object",
              "properties": {
                "start": { "type": "string" },
                "end": { "type": "string" }
              }
            }
          }
        },
        "authors": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name"],
            "properties": {
              "id": { "type": "string" },
              "sequence": { "type": "integer" },
              "name": { "type": "string" },
              "email": { "type": "string", "format": "email" },
              "orcid": { "type": "string" },
              "affiliations": { "type": "array", "items": { "type": "object" } }
            }
          }
        }
      }
    }
  }
}
```

---

## 2. XML Export Format

### File Extension: `.xml`
### MIME Type: `application/xml`

### Complete Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<metadata-export xmlns="http://example.org/metadata/1.0" 
                 version="1.0" 
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xsi:schemaLocation="http://example.org/metadata/1.0 metadata.xsd">
  
  <extraction>
    <timestamp>2026-05-04T14:31:00Z</timestamp>
    <source-file>paper_2024.pdf</source-file>
    <extraction-engine>llama2-7b-ollama</extraction-engine>
    <version>1.0.0</version>
  </extraction>
  
  <confidence-scores>
    <score field="title">0.98</score>
    <score field="doi">0.95</score>
    <score field="authors">0.92</score>
    <score field="affiliations">0.85</score>
    <score field="abstract">0.89</score>
    <score field="keywords">0.87</score>
    <score field="publication-date">0.93</score>
    <score field="journal-name">0.88</score>
    <overall>0.91</overall>
  </confidence-scores>
  
  <document id="meta_550e8400_e29b_41d4_a716_446655440002">
    <title>Deep Learning for Scientific Document Analysis</title>
    <doi>10.1145/3123456.3456789</doi>
    <abstract>This paper presents a novel approach to extracting structured metadata from scientific documents using deep learning techniques. We propose a multi-modal system that combines optical character recognition with natural language processing...</abstract>
    
    <keywords>
      <keyword>deep learning</keyword>
      <keyword>document analysis</keyword>
      <keyword>metadata extraction</keyword>
      <keyword>information retrieval</keyword>
      <keyword>machine learning</keyword>
    </keywords>
    
    <publication-info>
      <date>2024-01-15</date>
      <journal>
        <name>ACM Computing Surveys</name>
        <volume>57</volume>
        <issue>2</issue>
        <pages>
          <start>123</start>
          <end>156</end>
        </pages>
      </journal>
    </publication-info>
    
    <authors>
      <author id="auth_001" sequence="1">
        <name>Jane Smith</name>
        <email>jane.smith@mit.edu</email>
        <orcid>0000-0001-2345-6789</orcid>
        <affiliations>
          <affiliation id="aff_001">
            <institution>Massachusetts Institute of Technology</institution>
            <department>Computer Science and Artificial Intelligence Laboratory</department>
            <address>
              <city>Cambridge</city>
              <state>MA</state>
              <country>USA</country>
              <postal-code>02139</postal-code>
            </address>
          </affiliation>
        </affiliations>
      </author>
      
      <author id="auth_002" sequence="2">
        <name>John Doe</name>
        <email>john.doe@stanford.edu</email>
        <affiliations>
          <affiliation id="aff_002">
            <institution>Stanford University</institution>
            <department>Department of Computer Science</department>
            <address>
              <city>Stanford</city>
              <state>CA</state>
              <country>USA</country>
              <postal-code>94305</postal-code>
            </address>
          </affiliation>
          <affiliation id="aff_001">
            <institution>Massachusetts Institute of Technology</institution>
            <department>Computer Science and Artificial Intelligence Laboratory</department>
          </affiliation>
        </affiliations>
      </author>
    </authors>
  </document>
  
</metadata-export>
```

### XML Schema (XSD)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  
  <xs:element name="metadata-export">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="extraction" type="ExtractionType" minOccurs="1" maxOccurs="1"/>
        <xs:element name="confidence-scores" type="ConfidenceScoresType" minOccurs="0" maxOccurs="1"/>
        <xs:element name="document" type="DocumentType" minOccurs="1" maxOccurs="1"/>
      </xs:sequence>
      <xs:attribute name="version" type="xs:string" use="required"/>
    </xs:complexType>
  </xs:element>
  
  <xs:complexType name="ExtractionType">
    <xs:sequence>
      <xs:element name="timestamp" type="xs:dateTime"/>
      <xs:element name="source-file" type="xs:string"/>
      <xs:element name="extraction-engine" type="xs:string" minOccurs="0"/>
      <xs:element name="version" type="xs:string" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
  
  <xs:complexType name="DocumentType">
    <xs:sequence>
      <xs:element name="title" type="xs:string"/>
      <xs:element name="doi" type="xs:string" minOccurs="0"/>
      <xs:element name="abstract" type="xs:string" minOccurs="0"/>
      <xs:element name="keywords" type="KeywordsType" minOccurs="0"/>
      <xs:element name="publication-info" type="PublicationInfoType" minOccurs="0"/>
      <xs:element name="authors" type="AuthorsType" minOccurs="0"/>
    </xs:sequence>
    <xs:attribute name="id" type="xs:string"/>
  </xs:complexType>
  
</xs:schema>
```

---

## 3. TOON Export Format

### File Extension: `.toon`
### MIME Type: `text/plain`

### Complete Example

```toon
@extraction_metadata {
  timestamp: "2026-05-04T14:31:00Z"
  source_file: "paper_2024.pdf"
  extraction_engine: "llama2-7b-ollama"
  version: "1.0.0"
}

@confidence_scores {
  title: 0.98
  doi: 0.95
  authors: 0.92
  affiliations: 0.85
  abstract: 0.89
  keywords: 0.87
  publication_date: 0.93
  journal_name: 0.88
  overall: 0.91
}

@document {
  id: "meta_550e8400_e29b_41d4_a716_446655440002"
  
  title: "Deep Learning for Scientific Document Analysis"
  doi: "10.1145/3123456.3456789"
  
  abstract: "This paper presents a novel approach to extracting structured metadata 
from scientific documents using deep learning techniques. We propose a multi-modal 
system that combines optical character recognition with natural language processing..."
  
  keywords: [
    "deep learning"
    "document analysis"
    "metadata extraction"
    "information retrieval"
    "machine learning"
  ]
  
  publication_info {
    date: "2024-01-15"
    journal {
      name: "ACM Computing Surveys"
      volume: "57"
      issue: "2"
      pages {
        start: "123"
        end: "156"
      }
    }
  }
  
  authors: [
    {
      id: "auth_001"
      sequence: 1
      name: "Jane Smith"
      email: "jane.smith@mit.edu"
      orcid: "0000-0001-2345-6789"
      affiliations: [
        {
          id: "aff_001"
          institution: "Massachusetts Institute of Technology"
          department: "Computer Science and Artificial Intelligence Laboratory"
          address {
            city: "Cambridge"
            state: "MA"
            country: "USA"
            postal_code: "02139"
          }
        }
      ]
    }
    {
      id: "auth_002"
      sequence: 2
      name: "John Doe"
      email: "john.doe@stanford.edu"
      affiliations: [
        {
          id: "aff_002"
          institution: "Stanford University"
          department: "Department of Computer Science"
          address {
            city: "Stanford"
            state: "CA"
            country: "USA"
            postal_code: "94305"
          }
        }
        {
          id: "aff_001"
          institution: "Massachusetts Institute of Technology"
          department: "Computer Science and Artificial Intelligence Laboratory"
        }
      ]
    }
  ]
}
```

### TOON Format Specification

**Token-Oriented Object Notation (TOON)** is a human-readable data serialization format emphasizing explicit token definitions.

**Syntax Rules**:
- Objects defined with `@name { ... }` syntax
- Key-value pairs: `key: value`
- Arrays: `[ item1, item2, ... ]`
- Strings: Quoted with double quotes `"..."`
- Numbers: Unquoted decimal or integer (0.98, 57)
- Nested objects: `{ key { nested_key: value } }`
- Comments: `# comment line` (optional)
- Whitespace: Significant for readability; tabs/spaces equivalent

**Data Types**:
- **String**: `"value"`
- **Number**: `123` or `0.98`
- **Boolean**: `true` / `false`
- **Null**: `null`
- **Array**: `[ item1, item2 ]`
- **Object**: `{ key: value }`

---

## Format Comparison Table

| Aspect | JSON | XML | TOON |
|--------|------|-----|------|
| **Size** | Medium | Large (with tags) | Small (compact) |
| **Readability** | High | High | Very High |
| **Parse Speed** | Fast | Medium | Fast |
| **Schema Support** | JSON Schema | XSD | Ad-hoc |
| **Nesting Depth** | Unlimited | Unlimited | Limited |
| **Interoperability** | Excellent | Excellent | Good |
| **Human Edit** | Easy | Medium | Very Easy |

---

## Validation & Quality Assurance

### JSON Validation
- Valid JSON syntax (no trailing commas, proper quotes)
- All required fields present
- Confidence scores between 0.0 and 1.0
- Date strings in ISO 8601 format

### XML Validation
- Well-formed XML (matching tags, proper nesting)
- Validates against XSD schema
- All attributes properly escaped
- Namespace declarations correct

### TOON Validation
- Proper syntax (matching braces, colons)
- Quoted strings for text values
- Arrays properly bracketed
- No duplicate keys in objects

---

## File Size Guidelines

For a typical academic paper metadata:
- **JSON**: ~2-3 KB
- **XML**: ~3-5 KB
- **TOON**: ~1.5-2.5 KB

**Worst case** (comprehensive metadata with multiple affiliations):
- **JSON**: ~5-8 KB
- **XML**: ~8-12 KB
- **TOON**: ~4-6 KB

---

## Backwards Compatibility

- Format versions tracked in metadata (`"version": "1.0.0"`)
- Fields are additive (new fields don't break parsers)
- Deprecated fields marked with `@deprecated` comment
- Migration guides provided for major version changes

---

## References

- [JSON RFC 8259](https://tools.ietf.org/html/rfc8259)
- [W3C XML 1.0 Specification](https://www.w3.org/TR/xml/)
- [TOON Specification](http://example.org/toon/spec) (Token-Oriented Object Notation)
- [Schema.org ScholarlyArticle](https://schema.org/ScholarlyArticle)
