# Data Model: PDF Metadata Extraction System

**Phase**: 1 (Design & Contracts)  
**Date**: 2026-05-04  
**Status**: Complete

---

## Data Model Overview

The system manages three primary entity types throughout the user workflow: uploaded PDF documents, extracted metadata, and generated export files. All data is immutable once created (except user edits to metadata in the UI state).

---

## Entity Definitions

### 1. PDF Document

Represents an uploaded scientific article in PDF format.

```typescript
interface PDFDocument {
  id: string;                    // Unique identifier (UUID or timestamp-based)
  filename: string;              // Original filename (e.g., "paper_2024.pdf")
  fileSize: number;              // Size in bytes
  uploadTimestamp: Date;         // When user uploaded the file
  pageCount: number;             // Total number of pages
  textContent: string;           // Extracted raw text (cached for extraction)
  storageLocation?: string;      // File path or URL (temp storage on backend)
  validationStatus: 'valid' | 'invalid' | 'corrupted';
  validationError?: string;      // Error message if validation failed
}
```

**Relationships**:
- One-to-one with `ExtractionJob` (each PDF generates one extraction job)
- One-to-many with `ExtractedMetadata` fields (one PDF can have multiple metadata records if re-extracted)

**Constraints**:
- Maximum file size: 50 MB
- Format: PDF only (validated via MIME type and PDF header)
- Required fields: id, filename, fileSize, uploadTimestamp, validationStatus

**Lifecycle**:
1. **Uploaded**: File received, validation begins
2. **Valid**: PDF parsed, text extracted, ready for extraction
3. **Invalid**: Validation failed, error reported to user
4. **Extracted**: Metadata extraction job created and processing

---

### 2. Extraction Job

Tracks the state and progress of metadata extraction for a PDF.

```typescript
interface ExtractionJob {
  id: string;                           // Unique job identifier
  pdfDocumentId: string;                // Foreign key to PDFDocument
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout';
  startTime: Date;                      // When extraction began
  endTime?: Date;                       // When extraction completed
  elapsedTimeMs: number;                // Time taken (milliseconds)
  error?: {
    code: string;                       // Error code (e.g., 'EXTRACTION_TIMEOUT')
    message: string;                    // User-friendly error message
    details?: string;                   // Technical details for debugging
  };
  llmModel: string;                     // Model used (e.g., "llama2:7b-q4")
  retryCount: number;                   // Number of retries attempted
  rawLLMOutput: string;                 // Raw output from LLM (for debugging)
}
```

**Status Transitions**:
```
pending → processing → completed (success) → exported
       ↓                            ↓
       └──→ failed ──→ [user can retry] → pending
       └──→ timeout ──→ [user can retry] → pending
```

**Constraints**:
- Timeout: 30 seconds hard limit
- Max retries: 3 attempts
- Required fields: id, pdfDocumentId, status, startTime

**Lifecycle**:
1. **Pending**: Job queued, awaiting processing
2. **Processing**: Extraction actively running
3. **Completed**: All metadata extracted successfully
4. **Failed**: Extraction error occurred
5. **Timeout**: Extraction exceeded time limit

---

### 3. Extracted Metadata

The core data structure containing all extracted scientific article metadata.

```typescript
interface ExtractedMetadata {
  id: string;                          // Unique metadata record ID
  extractionJobId: string;             // Foreign key to ExtractionJob
  pdfDocumentId: string;               // Foreign key to PDFDocument
  extractionTimestamp: Date;           // When extraction completed
  
  // Core fields
  title: string;                       // Article title
  doi?: string;                        // Digital Object Identifier
  abstract?: string;                   // Paper abstract
  keywords: string[];                  // Keywords/tags (array of strings)
  journalName?: string;                // Publication venue
  publicationDate?: Date;              // Date published (ISO 8601)
  
  // Author information
  authors: Author[];                   // Array of author objects
  affiliations: Affiliation[];         // Array of affiliation objects
  
  // Confidence & quality metrics
  confidenceScores: {
    title: number;                     // 0-1, confidence in title extraction
    doi: number;
    authors: number;
    abstract: number;
    keywords: number;
    [key: string]: number;             // Score for each field
  };
  overallConfidence: number;           // 0-1, average confidence
  
  // Audit trail
  editedBy?: string;                   // User who edited (future: multi-user support)
  lastModified?: Date;                 // When last edited
  editHistory?: EditEvent[];           // Audit log of edits
}

interface Author {
  id?: string;                         // Author identifier
  name: string;                        // Full name
  email?: string;                      // Email address
  affiliationIds: string[];            // References to Affiliation records
}

interface Affiliation {
  id: string;                          // Unique affiliation ID
  institution: string;                 // Institution name
  department?: string;                 // Department name
  city?: string;                       // City
  country?: string;                    // Country
  postalCode?: string;                 // Postal code
}

interface EditEvent {
  fieldName: string;                   // Which field was edited
  oldValue: any;                       // Previous value
  newValue: any;                       // New value
  editedAt: Date;                      // When edited
  editedBy?: string;                   // User who edited
}
```

**Relationships**:
- Many-to-one with `ExtractionJob` (multiple extraction attempts possible)
- Many-to-one with `PDFDocument`
- One-to-one with `ExportedFiles` (one metadata record → one set of export files)

**Constraints**:
- Required fields: id, extractionJobId, title
- Optional but valuable: doi, abstract, keywords, authors, publicationDate
- Confidence scores: 0.0 to 1.0 (float)
- Keywords: minimum 1, typically 3-10

**Immutability**:
- Original extracted values immutable (stored as `originalValue`)
- User edits tracked in `editHistory` but don't overwrite original
- Can revert to original extracted values at any time

---

### 4. Exported Files

Represents the three generated output files (JSON, XML, TOON) for a metadata record.

```typescript
interface ExportedFiles {
  id: string;                          // Unique export record ID
  metadataId: string;                  // Foreign key to ExtractedMetadata
  generatedTimestamp: Date;            // When files were generated
  expiresAt?: Date;                    // Expiration time (optional, for server cleanup)
  
  // File contents or references
  files: {
    json: ExportFile;                  // JSON export
    xml: ExportFile;                   // XML export
    toon: ExportFile;                  // TOON export
  };
}

interface ExportFile {
  format: 'json' | 'xml' | 'toon';
  filename: string;                    // e.g., "metadata_2024-05-04.json"
  mimeType: string;                    // e.g., "application/json"
  fileSize: number;                    // Size in bytes
  contentHash: string;                 // SHA-256 hash for integrity verification
  content: string;                     // File contents (for client-side download)
  downloadUrl?: string;                // Server URL for download (if backend-hosted)
  generatedAt: Date;                   // Generation timestamp
}
```

**Relationships**:
- One-to-one with `ExtractedMetadata`
- Parent record deleted → files can be cleaned up after expiration

**File Format Specifications**: See [export-formats.md](contracts/export-formats.md)

---

## Validation Rules

### PDFDocument Validation
- **filename**: Non-empty string, max 255 characters
- **fileSize**: > 0 bytes, ≤ 50 MB (52,428,800 bytes)
- **uploadTimestamp**: Valid ISO 8601 timestamp
- **pageCount**: ≥ 1
- **validationStatus**: Must be one of: 'valid', 'invalid', 'corrupted'

### ExtractedMetadata Validation
- **title**: Non-empty string, max 500 characters
- **doi**: Optional, must match DOI pattern (10.XXXX/...)
- **keywords**: Array of 1-50 non-empty strings
- **authors**: Array of 1-100 Author objects
- **confidenceScores**: Object with values 0.0-1.0
- **publicationDate**: Valid ISO 8601 date or null
- **abstract**: Optional, max 5000 characters

### Author Validation
- **name**: Non-empty string, max 200 characters
- **email**: Optional, must be valid email format
- **affiliationIds**: Array of valid Affiliation IDs

### Affiliation Validation
- **institution**: Non-empty string, max 300 characters
- **department**: Optional, max 200 characters
- **country**: Optional, valid ISO 3166-1 country code

---

## State Transitions

### User Workflow State Machine

```
┌─────────────────────────────────────────────────────┐
│                   START (Empty UI)                   │
└────────────────────┬────────────────────────────────┘
                     │ Upload PDF
                     ↓
┌─────────────────────────────────────────────────────┐
│        PDF Uploaded & Displayed (Right Panel)        │
│    [Extract Button Enabled, Metadata Panel Empty]    │
└────────────────────┬────────────────────────────────┘
                     │ Click Extract Metadata
                     ↓
┌─────────────────────────────────────────────────────┐
│         Extraction In Progress (Loading State)       │
│    [Extract Button Disabled, Progress Indicator]     │
└────────────────┬──────────────────────────────────┬─┘
                 │                                   │
       Success   │                                   │ Failure/Timeout
                 ↓                                   ↓
    ┌────────────────────────┐         ┌────────────────────────┐
    │  Metadata Extracted    │         │   Extraction Failed    │
    │  (Left Panel Populated)│         │  (Error Message Show)  │
    │ [Review Mode Enabled]  │         │  [Retry Option]        │
    └───────────┬────────────┘         └────────────────────────┘
                │
        User edits fields, clicks Export
                │
                ↓
    ┌────────────────────────┐
    │  Files Generating      │
    │  (Export Loading State)│
    └───────────┬────────────┘
                │
                ↓
    ┌────────────────────────┐
    │  Export Complete       │
    │  [Download Buttons]    │
    │  [Start Over Option]   │
    └────────────────────────┘
```

---

## Data Storage Strategy

### Frontend (React State)
```typescript
interface AppState {
  pdf: {
    document: PDFDocument | null;
    currentPage: number;
    isLoading: boolean;
    error?: string;
  };
  extraction: {
    job: ExtractionJob | null;
    metadata: ExtractedMetadata | null;
    isLoading: boolean;
    error?: string;
  };
  export: {
    files: ExportedFiles | null;
    isLoading: boolean;
    error?: string;
  };
  ui: {
    activeTab: 'pdf' | 'metadata' | 'export';
    editingFieldId?: string;
    notifications: Notification[];
  };
}
```

### Backend Storage
- **Session storage**: Extract metadata, export files cached in temp directory (~1 hour TTL)
- **Logging**: All operations logged with timestamps and correlation IDs
- **No persistent database**: v1 single-user, files deleted after export

---

## Performance Considerations

### Memory Efficiency
- PDF files kept in memory only (max 50MB → manageable)
- Metadata objects small (<100KB typical)
- Export files generated on-demand, not pre-generated

### Indexing
- Not applicable (no database queries)
- Frontend filtering: O(n) where n = number of metadata fields (typically 8-10, negligible)

### Caching
- PDF text content cached after extraction (avoid re-extracting)
- Export files cached for 1 hour on backend
- Browser cache headers for static assets

---

## Data Privacy & Security

- No personally identifiable information (PII) beyond author names/emails from PDFs
- PDF files deleted immediately after metadata extraction (not persisted)
- Metadata stored in memory only (cleared on page refresh)
- No authentication/encryption required for v1 (single-user local)
- Export files can be downloaded securely (client-side or time-limited URLs)

---

## Future Extensibility

The data model is designed for future enhancements:
- **Multi-user**: Add `userId` to all entities, implement permission model
- **Persistence**: Add userId, timestamps for audit trail; migrate to database (PostgreSQL recommended)
- **Batch processing**: Support multiple PDFs; add `BatchJob` entity
- **Advanced metadata**: Add fields like citations, references, supplementary materials
- **ML improvements**: Track accuracy metrics per field for model training
- **Versioning**: Support multiple extraction attempts per PDF with comparison view

---

## Conclusion

Data model is normalized, validated, and ready for implementation. All entities have clear relationships and lifecycle management. No design conflicts with constitution principles.
