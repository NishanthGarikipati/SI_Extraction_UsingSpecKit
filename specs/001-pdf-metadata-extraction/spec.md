# Feature Specification: PDF Metadata Extraction UI

**Feature Branch**: `001-pdf-metadata-extraction`  
**Created**: 2026-05-04  
**Status**: Draft  
**Tech Stack**: React/TypeScript (frontend) + Python (backend with LLaMA 2/Ollama)  
**User Input**: Build an application for uploading PDFs, extracting metadata using RAG model, reviewing extracted data, and generating downloadable export files (JSON, XML, TOON)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Upload and Display PDF (Priority: P1)

A researcher needs to upload a scientific article PDF and see it rendered on the right side of the interface to verify the content before metadata extraction.

**Why this priority**: Core MVP functionality - users cannot proceed without uploading a document first. This is the entry point for the entire workflow.

**Independent Test**: Can be fully tested by uploading a valid PDF file and verifying it displays correctly on the right panel without requiring any other features to be implemented.

**Acceptance Scenarios**:

1. **Given** a user is on the application home page, **When** user clicks the upload button on the right side, **Then** a file picker dialog opens
2. **Given** a file picker dialog is open, **When** user selects a valid PDF file, **Then** the PDF is uploaded and displayed in the right panel with proper rendering
3. **Given** a PDF is displayed on the right side, **When** user scrolls through the PDF, **Then** all pages are visible and navigation works smoothly
4. **Given** a user uploads an invalid file, **When** the upload completes, **Then** an error message appears explaining the file must be a valid PDF
5. **Given** a PDF is already displayed, **When** user uploads a new PDF, **Then** the previous PDF is replaced with the new one

---

### User Story 2 - Extract Metadata Using RAG Model (Priority: P1)

After uploading a PDF, a researcher clicks an extract button to run the RAG model, which analyzes the document and extracts key scientific metadata automatically.

**Why this priority**: Core MVP functionality - metadata extraction is the primary value proposition. Without this, the application is just a PDF viewer.

**Independent Test**: Can be tested by uploading a PDF and clicking extract, then verifying that the system calls the RAG model backend and returns structured metadata without requiring export functionality.

**Acceptance Scenarios**:

1. **Given** a PDF is displayed on the right side, **When** user clicks the "Extract Metadata" button, **Then** the system shows a loading indicator
2. **Given** the extract button is clicked, **When** the RAG model processes the PDF, **Then** extraction completes within 30 seconds for typical academic PDFs
3. **Given** extraction is in progress, **When** the process completes successfully, **Then** the loading indicator disappears and extracted metadata is displayed
4. **Given** extraction fails or times out, **When** the error occurs, **Then** a user-friendly error message appears with retry option
5. **Given** extraction completes successfully, **When** the metadata is extracted, **Then** no data is lost and all fields are captured

---

### User Story 3 - Display and Review Extracted Metadata (Priority: P1)

The extracted metadata is displayed on the left side of the interface as an organized list of fields that the user can review, edit, and validate before final submission.

**Why this priority**: Critical for data quality - users must be able to review and correct any extraction errors before export. This ensures accuracy of exported data.

**Independent Test**: Can be tested independently by displaying mock extracted metadata and verifying UI layout, edit functionality, and field organization work correctly.

**Acceptance Scenarios**:

1. **Given** metadata extraction has completed, **When** the user views the left panel, **Then** all metadata fields are displayed in an organized, scannable list
2. **Given** extracted metadata is displayed, **When** a user clicks on a metadata field, **Then** the field becomes editable (text input, dropdown, or appropriate control)
3. **Given** a metadata field is being edited, **When** user makes changes and clicks elsewhere, **Then** changes are saved to the in-memory state
4. **Given** metadata has been extracted, **When** the user reviews all fields, **Then** the following metadata is displayed:
   - Article Title
   - DOI (Digital Object Identifier)
   - Authors (with individual edit capability for each author)
   - Author Affiliations (associated with each author)
   - Keywords/Tags
   - Abstract
   - Publication Date
   - Journal Name
5. **Given** multiple authors are extracted, **When** user views the authors section, **Then** each author and their affiliations are properly associated and displayed

---

### User Story 4 - Generate Export Files (Priority: P2)

After reviewing the metadata, the user clicks a submit/review button which generates three export files (JSON, XML, TOON) containing the extracted and validated metadata.

**Why this priority**: Essential for data sharing and downstream processing. Without export, the extracted data cannot be used in other systems.

**Independent Test**: Can be tested by generating export files and verifying file format, structure, and content correctness without requiring download functionality.

**Acceptance Scenarios**:

1. **Given** metadata has been extracted and reviewed, **When** user clicks the "Submit" or "Export" button, **Then** the system generates three files simultaneously
2. **Given** the export button is clicked, **When** file generation begins, **Then** a loading state is displayed to user
3. **Given** file generation completes successfully, **When** the process finishes, **Then** all three files (JSON, XML, TOON) are created with proper formatting
4. **Given** files are generated, **When** the user examines the JSON file, **Then** it contains valid JSON structure with all extracted metadata fields
5. **Given** files are generated, **When** the user examines the XML file, **Then** it contains valid XML structure with metadata organized in nested elements
6. **Given** files are generated, **When** the user examines the TOON file, **Then** it contains proper token-oriented object notation format with all metadata accessible

---

### User Story 5 - Download Generated Files (Priority: P2)

Users can download the generated export files (JSON, XML, TOON) to their local machine for integration with external systems or archival.

**Why this priority**: Enables practical use of extracted data. Without download capability, users cannot retrieve their exported files.

**Independent Test**: Can be tested by generating files and verifying download mechanism works, files are properly named, and content is intact.

**Acceptance Scenarios**:

1. **Given** export files have been generated, **When** the interface displays download options, **Then** three separate download buttons are available (one for each file type)
2. **Given** download buttons are available, **When** user clicks a download button, **Then** the corresponding file is downloaded to the user's default downloads folder
3. **Given** a file is downloaded, **When** the download completes, **Then** the filename includes a timestamp or document identifier for easy organization
4. **Given** multiple files are downloaded, **When** all three files are downloaded sequentially, **Then** each file is correctly formatted and contains complete metadata
5. **Given** files are downloaded, **When** user opens a downloaded file, **Then** the file is readable and contains the exact metadata that was extracted

---

### Edge Cases

- What happens when user uploads a PDF with scanned images only (no text) - can RAG model extract metadata?
- How does system handle corrupted or partially corrupted PDF files?
- What is the maximum file size for PDF uploads - how does system respond to oversized files?
- What happens if RAG model fails on specific sections of a document - does extraction continue or fully fail?
- Can user cancel extraction once it has begun?
- What happens if user uploads a new PDF while metadata extraction is in progress?
- How are special characters and non-ASCII text in author names handled in export files?
- What happens if all extracted metadata fields are empty?

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an upload button on the right side of the UI that accepts PDF files only
- **FR-002**: System MUST validate uploaded files as valid PDF documents before processing
- **FR-003**: System MUST display uploaded PDFs in a PDF viewer component on the right side of the UI with full page rendering
- **FR-004**: System MUST provide an "Extract Metadata" button that becomes active only after a PDF is successfully uploaded
- **FR-005**: System MUST send the uploaded PDF to a Python backend service running LLaMA 2/Ollama for RAG-based metadata extraction
- **FR-006**: System MUST extract the following metadata fields: Title, DOI, Authors, Affiliations, Keywords, Abstract, Publication Date, Journal Name
- **FR-007**: System MUST parse extracted metadata into structured fields and display each field on the left side UI panel
- **FR-008**: System MUST allow users to view extracted metadata in an organized list format with field labels
- **FR-009**: System MUST allow users to edit each extracted metadata field after extraction completion
- **FR-010**: System MUST persist edited metadata in memory until export is triggered
- **FR-011**: System MUST provide an "Submit/Export" button that generates JSON, XML, and TOON formatted files
- **FR-012**: System MUST generate valid JSON file containing all extracted metadata in standard JSON structure
- **FR-013**: System MUST generate valid XML file containing all extracted metadata in hierarchical XML structure
- **FR-014**: System MUST generate valid TOON (Token-Oriented Object Notation) file containing all extracted metadata
- **FR-015**: System MUST provide download buttons for each generated file (JSON, XML, TOON)
- **FR-016**: System MUST allow users to download files with appropriate MIME types and extensions
- **FR-017**: System MUST display loading indicators during PDF upload, metadata extraction, and file generation
- **FR-018**: System MUST display user-friendly error messages when upload, extraction, or export fails
- **FR-019**: System MUST handle PDF files up to 50MB in size without performance degradation
- **FR-020**: System MUST provide a clear visual layout with PDF on right and metadata on left, clearly distinguishing the two sections

### Key Entities

- **PDF Document**: Uploaded scientific article in PDF format with text content
  - Attributes: filename, file size, upload timestamp, page count
  - Relationships: one-to-one with ExtractionJob, one-to-many with ExtractedMetadata fields

- **Extracted Metadata**: Structured data parsed from PDF by RAG model
  - Attributes: title, DOI, authors (list), affiliations (list), keywords (list), abstract, publication_date, journal_name, confidence_scores
  - Relationships: many-to-one with PDF Document, one-to-one with ExportedFiles

- **Exported Files**: Generated output files from extracted metadata
  - Attributes: JSON content, XML content, TOON content, generation timestamp, file format
  - Relationships: one-to-one with Extracted Metadata

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can upload a PDF and see it rendered in the UI within 3 seconds (including network transfer for files under 10MB)
- **SC-002**: Metadata extraction completes for typical academic PDFs (5-20 pages) in under 30 seconds
- **SC-003**: Extracted metadata accuracy is 85% or higher for standard fields (title, authors, DOI) compared to manual review
- **SC-004**: Users can generate and download all three export files within 5 seconds after clicking submit
- **SC-005**: Downloaded files are valid and can be parsed by standard JSON, XML, and TOON parsers without errors
- **SC-006**: UI layout is responsive and functional on desktop browsers (Chrome, Firefox, Safari, Edge) at 1366x768 resolution minimum
- **SC-007**: System handles 90% of tested academic PDFs without extraction errors or application crashes
- **SC-008**: Users complete the entire workflow (upload → extract → review → export → download) in under 5 minutes for typical documents

---

## Assumptions

- Users have stable internet connectivity for uploading PDFs and communicating with backend services
- PDFs are primarily scientific articles with structured content (title, authors, abstract sections clearly defined)
- LLaMA 2/Ollama service will be available and accessible on the same network or via API
- Users have modern browsers with PDF rendering support (Chrome, Firefox, Safari, Edge on desktop)
- File downloads will be saved to user's default downloads folder managed by browser
- Maximum recommended file size is 50MB; larger files may experience performance degradation
- Token Oriented Object Notation (TOON) format follows standard conventions for object serialization
- The RAG model has been pre-trained or fine-tuned on scientific article data for optimal extraction accuracy
- Mobile/tablet support is out of scope for v1 (desktop-only application)
- Authentication and multi-user access is out of scope for v1 (single user local deployment)
- PDF has actual text content (not image scans) for reliable metadata extraction
- Backend infrastructure (Python service running Ollama) will be deployed separately and made available to frontend
