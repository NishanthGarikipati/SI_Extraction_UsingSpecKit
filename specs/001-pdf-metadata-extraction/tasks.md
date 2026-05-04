# Tasks: PDF Metadata Extraction UI

**Input**: Design documents from `specs/001-pdf-metadata-extraction/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅  
**Branch**: `001-pdf-rag-metadata-extractor`  
**Status**: Ready for Implementation

---

## Format Reference

**Checklist Format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[TaskID]**: Sequential number (T001, T002...) in execution order
- **[P]**: Task is parallelizable (independent files, no blocking dependencies)
- **[Story]**: User story identifier (US1, US2, US3, US4, US5 - or no label for Setup/Foundational)
- **File paths**: Exact locations for implementation

---

## Phase 1: Setup & Project Initialization

**Purpose**: Initialize backend and frontend projects with dependencies and tooling

### Backend Setup

- [ ] T001 Create backend directory structure per plan: `backend/src/{models,services,api,utils,prompts}` and `backend/tests/{unit,integration}`
- [ ] T002 Initialize Python virtual environment: `backend/venv` with Python 3.10+
- [ ] T003 Create `backend/requirements.txt` with core dependencies: FastAPI, Uvicorn, Pydantic, pdfplumber, PyPDF2, python-multipart, pytest, langchain, ollama, requests
- [ ] T004 Create `backend/.env` with configuration: OLLAMA_HOST, OLLAMA_MODEL, EXTRACTION_TIMEOUT_SECONDS, API_HOST, API_PORT, FRONTEND_URL, ALLOW_ORIGINS, LOG_LEVEL
- [ ] T005 [P] Create `backend/pyproject.toml` with project metadata and build configuration
- [ ] T006 [P] Configure `backend/pytest.ini` and test fixtures in `backend/tests/conftest.py`
- [ ] T007 [P] Create `backend/src/config.py` with Pydantic settings for all environment variables

### Frontend Setup

- [ ] T008 Create frontend directory structure per plan: `frontend/src/{components,pages,services,types,hooks,styles}` and `frontend/tests/{unit,integration,e2e}`
- [ ] T009 Initialize Vite + React + TypeScript project: `frontend/package.json`, `vite.config.ts`, `tsconfig.json`
- [ ] T010 Create `frontend/package.json` with core dependencies: react, react-dom, typescript, react-pdf, tailwindcss, zustand, react-hook-form, axios, vitest, @testing-library/react, playwright
- [ ] T011 [P] Configure Tailwind CSS: `frontend/tailwind.config.ts`, `frontend/postcss.config.cjs`, `frontend/src/styles/index.css`
- [ ] T012 [P] Create `frontend/vite.config.ts` with React plugin, dev server proxy to backend (`/api` → `http://localhost:8000`)
- [ ] T013 [P] Create `frontend/.env.local` with VITE_API_URL=http://localhost:8000/api
- [ ] T014 [P] Create `frontend/vitest.config.ts` and `playwright.config.ts` for testing

### Shared Tooling

- [ ] T015 Create `.gitignore` to exclude node_modules, venv, build outputs, .env files
- [ ] T016 Create `docs/DEV_SETUP.md` with detailed development environment setup instructions
- [ ] T017 [P] Create Makefile or shell scripts for common tasks (install, dev, test, build, format, lint)

---

## Phase 2: Foundational Infrastructure

**Purpose**: Core infrastructure that MUST be complete before user story implementation

**⚠️ CRITICAL**: All Phase 1 tasks MUST complete and this entire phase MUST complete before US1 work begins

### Backend Core Infrastructure

- [ ] T018 Create `backend/src/main.py` FastAPI application entry point with CORS middleware configured from settings
- [ ] T019 Create `backend/src/api/routes.py` with stub endpoints: GET /health, POST /extract, GET /extract/{job_id}, POST /export, GET /download/{export_id}/{format}
- [ ] T020 [P] Create `backend/src/models/metadata.py` with Pydantic models: Author, Affiliation, ExtractedMetadata, ConfidenceScores (from contracts/metadata-schema.json)
- [ ] T021 [P] Create `backend/src/models/extraction_result.py` with ExtractionJob, ExtractResponse, StatusResponse models
- [ ] T022 Create `backend/src/services/pdf_processor.py` with PDF validation and text extraction utilities (uses pdfplumber, PyPDF2)
- [ ] T023 [P] Create `backend/src/services/rag_extractor.py` with LLaMA 2/Ollama integration for metadata extraction
- [ ] T024 [P] Create `backend/src/services/metadata_parser.py` with structured parsing of LLM output to ExtractedMetadata
- [ ] T025 [P] Create `backend/src/services/export_generator.py` with JSON, XML, and TOON file generation functions
- [ ] T026 Create `backend/src/utils/logging.py` with structured logging setup and correlation IDs
- [ ] T027 [P] Create `backend/src/utils/validators.py` with PDF file validation, size limits, format checks
- [ ] T028 Create `backend/src/prompts/extraction_prompt.txt` with LLM prompt template for metadata extraction (includes examples and structured instructions)
- [ ] T029 Implement `backend/src/api/health.py` health check endpoint returning service status including Ollama connectivity
- [ ] T030 [P] Create error handling middleware in `backend/src/main.py` with standardized error response format from contracts/api-specification.md

### Frontend Core Infrastructure

- [ ] T031 Create `frontend/src/main.tsx` React entry point and `frontend/index.html` root HTML file
- [ ] T032 Create `frontend/src/types/index.ts` with TypeScript interfaces: PDFDocument, ExtractionJob, ExtractedMetadata, Author, Affiliation, AppState (from data-model.md)
- [ ] T033 [P] Create `frontend/src/types/api.ts` with API request/response types from contracts/api-specification.md
- [ ] T034 Create `frontend/src/services/api.ts` API client with methods: uploadPDF(), getExtractionStatus(), generateExport(), downloadFile()
- [ ] T035 [P] Create `frontend/src/services/fileExport.ts` client-side export utilities (JSON, XML, TOON formatting as fallback)
- [ ] T036 Create `frontend/src/hooks/useAppState.ts` using Zustand for global state management (PDF, extraction job, metadata, export)
- [ ] T037 [P] Create `frontend/src/hooks/useExtraction.ts` custom hook for extraction workflow (upload → extract → poll → complete)
- [ ] T038 [P] Create `frontend/src/hooks/useFileUpload.ts` custom hook for PDF file upload validation and handling
- [ ] T039 Create `frontend/src/pages/App.tsx` main application component with split-panel layout (left: metadata, right: PDF)
- [ ] T040 [P] Create `frontend/src/components/UploadArea.tsx` component for PDF upload UI with drag-drop support
- [ ] T041 [P] Create `frontend/src/components/PDFViewer.tsx` component wrapper around react-pdf for displaying uploaded PDFs
- [ ] T042 Create `frontend/src/components/MetadataPanel.tsx` component for displaying extracted metadata in organized list

### Foundational Testing Infrastructure

- [ ] T043 Create `backend/tests/conftest.py` with pytest fixtures: mock Ollama service, sample PDFs, test metadata
- [ ] T044 [P] Create `backend/tests/unit/test_validators.py` with tests for PDF validation, file size checks
- [ ] T045 [P] Create `backend/tests/unit/test_models.py` with tests for Pydantic model validation
- [ ] T046 Create `frontend/tests/unit/components.test.tsx` basic component rendering tests for UploadArea, PDFViewer
- [ ] T047 [P] Create `frontend/tests/e2e/health.spec.ts` Playwright test verifying backend health endpoint

**Checkpoint**: Foundation complete - US1 implementation can now begin

---

## Phase 3: User Story 1 - Upload and Display PDF (Priority: P1) 🎯 MVP

**Goal**: Researcher can upload a scientific PDF and see it displayed on the right panel, ready for extraction

**Independent Test**: Upload valid PDF → verify rendering on right panel without extraction or export features

**Success Criteria**: 
- PDF displays within 3 seconds
- User can navigate through all pages
- Error handling for invalid files
- Previous PDF replaced when new one uploaded

### US1 - Backend Tasks

- [ ] T048 [US1] Implement `backend/src/api/routes.py POST /extract` endpoint: accept multipart PDF upload, validate file, store temporarily, return job_id
- [ ] T049 [US1] Implement PDF text extraction in `backend/src/services/pdf_processor.py`: extract_text_from_pdf() using pdfplumber, get page count, validate content exists
- [ ] T050 [P] [US1] Create `backend/src/models/job_models.py` with ExtractionJob model and in-memory job store (dict, keyed by job_id)
- [ ] T051 [US1] Implement `backend/src/api/routes.py GET /extract/{job_id}` with polling support: return status, elapsed time, estimated remaining time
- [ ] T052 [US1] Create unit tests in `backend/tests/unit/test_pdf_processor.py`: test_valid_pdf_extraction(), test_invalid_pdf_rejected(), test_pdf_size_limit()
- [ ] T053 [US1] Create integration test in `backend/tests/integration/test_extract_endpoint.py`: test_upload_pdf_returns_job_id(), test_poll_extraction_status()

### US1 - Frontend Tasks

- [ ] T054 [US1] Implement PDF upload handler in `frontend/src/hooks/useFileUpload.ts`: validate file type, size check (< 50MB), call API uploadPDF()
- [ ] T055 [P] [US1] Implement `frontend/src/components/PDFViewer.tsx` full react-pdf integration: display all pages, navigation controls (prev/next), zoom, page indicator
- [ ] T056 [P] [US1] Implement error boundary and error display: `frontend/src/components/ErrorDisplay.tsx` showing user-friendly error messages
- [ ] T057 [US1] Implement state management in `frontend/src/hooks/useAppState.ts`: store PDF document, current page, loading state, error state
- [ ] T058 [P] [US1] Implement `frontend/src/components/LoadingIndicator.tsx` with progress/spinner for file upload
- [ ] T059 [US1] Create comprehensive styling in `frontend/src/styles/index.css`: split-panel layout, responsive grid, PDF viewer container styling
- [ ] T060 [US1] Create unit tests in `frontend/tests/unit/pdf-viewer.test.tsx`: test_pdf_upload_success(), test_pdf_upload_failure(), test_page_navigation()
- [ ] T061 [US1] Create E2E test in `frontend/tests/e2e/upload-pdf.spec.ts` using Playwright: test_upload_display_workflow()

### US1 - Testing & QA

- [ ] T062 [US1] Create test fixtures in `backend/tests/fixtures/`: sample PDFs (valid, invalid, too-large, corrupted)
- [ ] T063 [US1] Manual QA: Test upload with various PDF sizes, formats, verify error messages clear and actionable
- [ ] T064 [US1] Performance validation: Verify PDF upload + display < 3 seconds for 10MB PDF on target hardware

**Checkpoint**: US1 Complete - Users can upload and view PDFs

---

## Phase 4: User Story 2 - Extract Metadata Using RAG Model (Priority: P1) 🎯 MVP

**Goal**: After uploading PDF, researcher clicks Extract Metadata button; system calls LLaMA 2/Ollama and displays extracted metadata on left panel

**Independent Test**: Upload PDF → click extract → verify backend calls Ollama and returns structured metadata

**Success Criteria**:
- Extraction completes in < 30 seconds
- 85%+ accuracy on title, authors, DOI fields
- Graceful error handling with retry option
- Loading indicator shows progress

### US2 - Backend Tasks

- [ ] T065 [US2] Implement `backend/src/services/rag_extractor.py`: initialize Ollama client, create extraction_prompt template, call LLM with proper error handling
- [ ] T066 [US2] Implement `backend/src/services/metadata_parser.py`: parse LLM output (handle variations in formatting), extract title, DOI, authors, keywords, etc.
- [ ] T067 [US2] Create `backend/src/prompts/extraction_prompt.txt` with structured prompt: examples, field instructions, output format specification for JSON parsing
- [ ] T068 [US2] Implement extraction job coordinator in `backend/src/services/job_manager.py`: manage job lifecycle (pending → processing → completed/failed), handle retries (max 3)
- [ ] T069 [P] [US2] Implement timeout handling in `backend/src/services/job_manager.py`: enforce 30-second hard limit, return timeout error if exceeded
- [ ] T070 [US2] Update `backend/src/api/routes.py GET /extract/{job_id}`: return full metadata on completion, error details on failure, retry count
- [ ] T071 [US2] Implement confidence scoring in `backend/src/services/metadata_parser.py`: calculate per-field confidence (0.0-1.0) based on extraction certainty
- [ ] T072 [US2] Create unit tests in `backend/tests/unit/test_rag_extractor.py`: test_ollama_connection(), test_prompt_construction(), test_metadata_parsing()
- [ ] T073 [US2] Create integration test in `backend/tests/integration/test_extraction_pipeline.py`: test_end_to_end_extraction(), test_extraction_timeout(), test_extraction_retry()
- [ ] T074 [US2] Create mock Ollama tests in `backend/tests/integration/test_rag_extractor_mock.py`: test with mocked LLM responses for consistent CI testing

### US2 - Frontend Tasks

- [ ] T075 [US2] Implement extract metadata button in `frontend/src/components/ExtractionControls.tsx`: active only after PDF uploaded, disabled during extraction
- [ ] T076 [US2] Implement polling logic in `frontend/src/hooks/useExtraction.ts`: poll extraction status every 1 second, update state, retry on failure
- [ ] T077 [P] [US2] Create `frontend/src/components/ExtractionProgress.tsx`: show loading spinner, elapsed time, estimated remaining time, cancel option
- [ ] T078 [US2] Implement error recovery in `frontend/src/hooks/useExtraction.ts`: display error message, retry button, retry counter
- [ ] T079 [P] [US2] Create `frontend/src/components/RetryButton.tsx` component with exponential backoff for failed extractions
- [ ] T080 [US2] Integrate extraction results into app state: store in `useAppState()`, trigger UI update on completion
- [ ] T081 [US2] Create unit tests in `frontend/tests/unit/extraction.test.tsx`: test_extraction_polling(), test_extraction_error_retry()
- [ ] T082 [US2] Create E2E test in `frontend/tests/e2e/extraction.spec.ts`: test_extract_metadata_workflow() with mocked backend

### US2 - Testing & QA

- [ ] T083 [US2] Test with diverse academic PDFs: computer science, biology, physics papers (10+ samples)
- [ ] T084 [US2] Validate extraction accuracy: compare 10 PDFs against manual ground truth, achieve 85%+ target
- [ ] T085 [US2] Performance testing: measure extraction time, verify < 30s on target hardware
- [ ] T086 [US2] Error scenario testing: invalid PDFs, Ollama unavailable, network errors, timeout handling

**Checkpoint**: US2 Complete - Metadata extraction working end-to-end

---

## Phase 5: User Story 3 - Display and Review Extracted Metadata (Priority: P1) 🎯 MVP

**Goal**: Extracted metadata displays on left panel in organized list; user can review and edit each field

**Independent Test**: Display mock metadata → verify all fields shown → verify edit functionality works

**Success Criteria**:
- All 8 fields clearly labeled and displayed
- Each field editable with appropriate input control
- Changes saved to in-memory state
- Authors and affiliations properly associated

### US3 - Backend Tasks

- [ ] T087 [US3] No backend changes needed for display/review (uses existing metadata from US2)

### US3 - Frontend Tasks

- [ ] T088 [US3] Create `frontend/src/components/MetadataList.tsx` component: render all extracted fields in organized list with sections (Basic Info, Authors, etc.)
- [ ] T089 [US3] Implement `frontend/src/components/MetadataField.tsx` reusable component: label, value display, edit toggle, input control
- [ ] T090 [P] [US3] Create field-specific input components:
  - `TextFieldInput.tsx` for title, abstract, DOI
  - `DateFieldInput.tsx` for publication_date
  - `TagsFieldInput.tsx` for keywords (array of strings)
  - `AuthorsFieldInput.tsx` for authors with affiliations
  - `AffiliationsFieldInput.tsx` for affiliations list
- [ ] T091 [US3] Implement state mutation for metadata edits in `frontend/src/hooks/useAppState.ts`: updateMetadataField(fieldName, value)
- [ ] T092 [US3] Create `frontend/src/components/AuthorsSection.tsx`: display authors with edit capability, show affiliations per author, add/remove author
- [ ] T093 [P] [US3] Create `frontend/src/components/AffiliationsSection.tsx`: display affiliations with edit capability, institution/department/address fields
- [ ] T094 [US3] Implement validation for edits: DOI format validation, email validation, required field checks
- [ ] T095 [P] [US3] Create `frontend/src/components/ConfidenceIndicator.tsx`: show confidence score per field (0-100%), color-code by confidence level
- [ ] T096 [US3] Create comprehensive styling for metadata panel: Tailwind CSS classes, dark mode support, responsive column layout
- [ ] T097 [US3] Create unit tests in `frontend/tests/unit/metadata-display.test.tsx`: test_metadata_field_edit(), test_author_affiliation_association()
- [ ] T098 [US3] Create unit tests for field validation: test_doi_format_validation(), test_email_validation(), test_required_fields()
- [ ] T099 [US3] Create E2E test in `frontend/tests/e2e/metadata-review.spec.ts`: test_edit_and_save_metadata_workflow()

### US3 - Testing & QA

- [ ] T100 [US3] Manual QA: Edit various fields, verify changes reflected, reload and verify persistence in session
- [ ] T101 [US3] Accessibility testing: keyboard navigation through all fields, screen reader testing, color contrast validation

**Checkpoint**: US3 Complete - MVP fully functional (upload → extract → review)

---

## Phase 6: User Story 4 - Generate Export Files (Priority: P2)

**Goal**: After reviewing metadata, user clicks Export button; system generates JSON, XML, TOON files

**Independent Test**: Generate export files → verify all three formats valid and well-formed

**Success Criteria**:
- All three files generated correctly
- JSON validates against schema
- XML well-formed and valid
- TOON proper syntax and parseable

### US4 - Backend Tasks

- [ ] T102 [US4] Implement `backend/src/services/export_generator.py generate_json()`: serialize metadata to valid JSON per contracts/export-formats.md, include confidence scores and metadata
- [ ] T103 [P] [US4] Implement `backend/src/services/export_generator.py generate_xml()`: serialize metadata to valid XML per contracts/export-formats.md, include namespace declarations
- [ ] T104 [P] [US4] Implement `backend/src/services/export_generator.py generate_toon()`: serialize metadata to TOON format per contracts/export-formats.md
- [ ] T105 [US4] Implement `backend/src/api/routes.py POST /export` endpoint: accept metadata_id, formats list, call export generator, return file objects with MIME types
- [ ] T106 [US4] Implement file validation: validate generated JSON against schema, validate XML syntax, validate TOON syntax
- [ ] T107 [P] [US4] Create export result model in `backend/src/models/export_models.py`: ExportedFiles, ExportFile objects with checksums
- [ ] T108 [US4] Create unit tests in `backend/tests/unit/test_export_generator.py`: test_json_generation(), test_xml_generation(), test_toon_generation()
- [ ] T109 [P] [US4] Create validation tests: test_json_schema_validation(), test_xml_well_formedness(), test_toon_syntax()
- [ ] T110 [US4] Create integration test in `backend/tests/integration/test_export_endpoint.py`: test_export_all_formats(), test_export_validation()

### US4 - Frontend Tasks

- [ ] T111 [US4] Create `frontend/src/components/ExportButton.tsx` component: button for initiating export, disabled until metadata ready
- [ ] T112 [US4] Implement export handler in `frontend/src/hooks/useExport.ts`: call API exportMetadata(), handle response, store in app state
- [ ] T113 [P] [US4] Create `frontend/src/components/ExportProgress.tsx`: show loading indicator, file generation status for each format
- [ ] T114 [US4] Implement export result display in `frontend/src/components/ExportResult.tsx`: show generated files, preview buttons, download buttons
- [ ] T115 [P] [US4] Create file format info component `frontend/src/components/FormatInfo.tsx`: brief description of each format (JSON, XML, TOON)
- [ ] T116 [US4] Create unit tests in `frontend/tests/unit/export.test.tsx`: test_export_api_call(), test_export_result_display()
- [ ] T117 [US4] Create E2E test in `frontend/tests/e2e/export.spec.ts`: test_export_files_generated_workflow()

### US4 - Testing & QA

- [ ] T118 [US4] Validate generated files against schemas: JSON with JSON Schema, XML with XSD
- [ ] T119 [US4] Test export with various metadata scenarios: minimal fields, all fields populated, special characters in author names
- [ ] T120 [US4] Performance validation: export generation < 5 seconds for typical metadata

**Checkpoint**: US4 Complete - Export files generating successfully

---

## Phase 7: User Story 5 - Download Generated Files (Priority: P2)

**Goal**: User can download all three generated files to local machine

**Independent Test**: Generate files → download each one → verify file integrity and format

**Success Criteria**:
- All three files download successfully
- Filenames include timestamp/identifier
- Downloaded files readable and intact
- MIME types correct

### US5 - Backend Tasks

- [ ] T121 [US5] Implement `backend/src/api/routes.py GET /download/{export_id}/{format}` endpoint: return file with proper Content-Type header, Content-Disposition attachment
- [ ] T122 [US5] Implement file lookup and serving in `backend/src/services/file_service.py`: locate export file, validate format, return with correct MIME type
- [ ] T123 [P] [US5] Implement filename generation in `backend/src/utils/filename.py`: create descriptive filenames with timestamp (e.g., "metadata_2026-05-04_14-31-00.json")
- [ ] T124 [US5] Implement file cleanup in `backend/src/services/file_service.py`: expired files (> 1 hour old) deleted automatically
- [ ] T125 [P] [US5] Create unit tests in `backend/tests/unit/test_file_service.py`: test_file_lookup(), test_filename_generation(), test_mime_types()
- [ ] T126 [US5] Create integration test in `backend/tests/integration/test_download_endpoint.py`: test_download_json(), test_download_xml(), test_download_toon()

### US5 - Frontend Tasks

- [ ] T127 [US5] Create `frontend/src/components/DownloadButtons.tsx` component: three buttons (one per format) with download icons
- [ ] T128 [US5] Implement download handler in `frontend/src/services/fileDownload.ts`: call API download endpoint, trigger browser download, handle errors
- [ ] T129 [P] [US5] Create `frontend/src/components/DownloadStatus.tsx`: show download progress, success notification, error handling
- [ ] T130 [US5] Implement retry logic for failed downloads: show error message, retry button with exponential backoff
- [ ] T131 [P] [US5] Create success notification in `frontend/src/components/DownloadNotification.tsx`: confirmation with file size, format
- [ ] T132 [US5] Create unit tests in `frontend/tests/unit/download.test.tsx`: test_download_api_call(), test_browser_download_trigger()
- [ ] T133 [US5] Create E2E test in `frontend/tests/e2e/download.spec.ts`: test_download_files_workflow()

### US5 - Testing & QA

- [ ] T134 [US5] Manual QA: Download all three formats, verify files readable in appropriate applications
- [ ] T135 [US5] File integrity testing: calculate checksums of downloaded files, verify match server checksums
- [ ] T136 [US5] Browser compatibility: test downloads on Chrome, Firefox, Safari, Edge

**Checkpoint**: US5 Complete - Full user workflow end-to-end

---

## Phase 8: Cross-Cutting Concerns & Polish

**Purpose**: Quality gates, performance, accessibility, documentation

### Testing & Quality Assurance

- [ ] T137 Achieve 80%+ unit test coverage for backend: `pytest --cov=backend/src/` target 80%+
- [ ] T138 Achieve 80%+ unit test coverage for frontend: `npm run test -- --coverage` target 80%+
- [ ] T139 Create comprehensive E2E test suite in `frontend/tests/e2e/full-workflow.spec.ts`: test complete user journey upload → extract → review → export → download
- [ ] T140 Create performance benchmarks in `backend/tests/performance/` and `frontend/tests/performance/`: measure latency, memory, throughput
- [ ] T141 Run Lighthouse audit on frontend: target scores ≥ 90 for Performance, Accessibility, Best Practices
- [ ] T142 Accessibility audit: WCAG 2.1 AA compliance using axe-core and manual testing
- [ ] T143 Security audit: check for XSS vulnerabilities, CSRF tokens, input sanitization

### Performance Optimization

- [ ] T144 Optimize PDF viewer: lazy-load pages, implement caching, measure FCP/LCP < 1.5s target
- [ ] T145 Optimize frontend bundle: code splitting for export utilities, tree-shake unused code, target < 200KB gzipped
- [ ] T146 Implement frontend caching: service worker for offline support, cache static assets
- [ ] T147 Optimize backend: database query optimization (if applicable), connection pooling, response caching
- [ ] T148 Monitor and optimize extraction latency: profile LLM inference, measure p95 < 30s

### Error Handling & Resilience

- [ ] T149 Implement comprehensive error handling across all API endpoints: proper HTTP status codes, error response format
- [ ] T150 Implement graceful degradation: if Ollama unavailable, show clear message with alternatives
- [ ] T151 Implement request validation: validate all inputs per OpenAPI spec, return 400 errors with validation details
- [ ] T152 Implement rate limiting (preparation for production): tracking infrastructure in place, documented limits

### Documentation

- [ ] T153 Update `docs/API.md`: complete API documentation with examples, generated from OpenAPI spec
- [ ] T154 Update `docs/ARCHITECTURE.md`: system architecture diagram, data flow, component interactions
- [ ] T155 Create `docs/DEPLOYMENT.md`: production deployment guide, environment setup, scaling considerations
- [ ] T156 Create `docs/TROUBLESHOOTING.md`: common issues, solutions, debugging tips
- [ ] T157 Update `README.md`: project overview, quick start, links to detailed documentation
- [ ] T158 Create `CONTRIBUTING.md`: development workflow, code style guidelines, testing requirements

### Build & Release

- [ ] T159 Configure CI/CD pipeline (GitHub Actions): run tests on every PR, build, deploy to staging
- [ ] T160 Create Docker configuration: `Dockerfile` for backend, `docker-compose.yml` for full stack local development
- [ ] T161 Configure code quality gates: linting (flake8, eslint), formatting (black, prettier), type checking (mypy, tsc)
- [ ] T162 Create pre-commit hooks: enforce linting, formatting, tests before commit
- [ ] T163 Set up release versioning: semantic versioning, changelog generation, automated releases

### Final Integration & QA

- [ ] T164 Full end-to-end testing: test all user stories together in complete workflow
- [ ] T165 Cross-browser testing: verify functionality on Chrome, Firefox, Safari, Edge (latest versions)
- [ ] T166 Load testing: verify system handles concurrent extraction requests, scaling limits
- [ ] T167 User acceptance testing: test with real academic PDFs, real researchers if possible
- [ ] T168 Documentation review: verify all docs current and accurate
- [ ] T169 Final security review: penetration testing, vulnerability scanning

---

## Phase 9: Future Enhancements (Out of Scope v1)

These are tracked for future iterations but NOT part of v1 MVP:

- [ ] Multi-user support with authentication and authorization
- [ ] Batch processing of multiple PDFs
- [ ] Advanced metadata fields (citations, references, supplementary materials)
- [ ] Batch export with various output formats
- [ ] Metadata comparison view (extracted vs. ground truth)
- [ ] Machine learning model improvement based on feedback
- [ ] Mobile UI support
- [ ] Cloud deployment options
- [ ] Integration with external metadata repositories (Crossref, PubMed, etc.)
- [ ] Metadata deduplication and merge tools

---

## Dependency Graph & Execution Strategy

### Critical Path (Blocking Dependencies)

```
Phase 1 (Setup) 
    ↓
Phase 2 (Foundational Infrastructure)
    ↓
Phase 3 (US1: Upload & Display) [P1 - MVP Core]
    ↓
Phase 4 (US2: Extract Metadata) [P1 - MVP Core]
    ↓
Phase 5 (US3: Review Metadata) [P1 - MVP Complete]
    ↓
Phase 6 (US4: Generate Export) [P2 - Enhancement]
    ↓
Phase 7 (US5: Download Files) [P2 - Enhancement]
    ↓
Phase 8 (Polish & Cross-Cutting)
```

### Parallel Execution Opportunities

Within each phase, tasks marked [P] can execute in parallel:

**Phase 1**: T005, T006, T007, T011, T012, T013, T014 (frontend setup parallelizable)

**Phase 2**: 
- Backend: T020, T021, T022, T023, T024, T025, T027, T030 (models and services parallelizable)
- Frontend: T040, T041, T042 (components parallelizable)
- Testing: T044, T045 (unit tests parallelizable)

**Phase 3+**: Individual field components and services can be parallelized by developer

### Recommended Execution Order

1. **Solo developer**: Follow sequential order (Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8)
2. **Two developers**: 
   - Developer A: Backend (Phases 1-2, backend tasks in 3-7)
   - Developer B: Frontend (Phases 1-2, frontend tasks in 3-7)
3. **Team of 4+**: 
   - Full parallelization within phases
   - 2 backend developers, 2 frontend developers
   - QA engineer runs tests after each phase

---

## Success Metrics & Acceptance Criteria

### MVP Success (Phase 5 Complete)
- ✅ User can upload PDF and see it displayed
- ✅ Metadata extraction working end-to-end
- ✅ User can review and edit all 8 metadata fields
- ✅ All 80%+ unit test coverage achieved
- ✅ E2E workflow tests passing

### Full Release Success (Phase 8 Complete)
- ✅ All 5 user stories implemented and tested
- ✅ 80%+ unit test coverage across codebase
- ✅ E2E tests covering all workflows
- ✅ Performance targets met (< 3s upload, < 30s extraction, < 5s export)
- ✅ WCAG 2.1 AA accessibility compliance
- ✅ Lighthouse audit scores ≥ 90
- ✅ Complete documentation
- ✅ Zero critical security vulnerabilities

---

## Effort Estimates

**Total Effort**: Approximately 160-200 hours of development work

### Phase Breakdown
- Phase 1 (Setup): 8-10 hours
- Phase 2 (Foundational): 20-25 hours
- Phase 3 (US1): 25-30 hours
- Phase 4 (US2): 30-35 hours
- Phase 5 (US3): 25-30 hours
- Phase 6 (US4): 15-20 hours
- Phase 7 (US5): 10-15 hours
- Phase 8 (Polish): 20-25 hours

### Team Composition Recommendations
- **1 developer**: 12-14 weeks at 15-20 hours/week
- **2 developers**: 6-7 weeks (1 backend, 1 frontend)
- **3+ developers**: 4-5 weeks (full parallelization)

---

## Next Steps

1. ✅ Review all tasks and effort estimates
2. ✅ Assign tasks to team members
3. ✅ Set up development environment per quickstart.md
4. ✅ Begin Phase 1 setup tasks
5. ✅ Complete Phase 2 foundational infrastructure
6. ✅ Implement Phase 3-5 (MVP)
7. ✅ Deploy and get user feedback
8. ✅ Implement Phase 6-7 (Enhancements)
9. ✅ Polish and release

---

## Task Tracking Notes

**Status Tracking**:
- Mark each task complete ✅ as it passes code review and automated tests
- Move stalled tasks to priority review if blocked for > 1 day
- Update effort estimates based on actual hours after first phase

**Code Review Gates** (before marking complete):
- All tests passing
- Code coverage ≥ 80% (or task-specific coverage)
- Linting and formatting passing
- Minimum 1 peer review approval
- No TODOs or FIXMEs in final code

**Definition of Done**:
- Code written per specification
- Unit tests written and passing (80%+ coverage)
- Integration tests passing
- E2E tests passing (for user-facing features)
- Documentation updated
- Code reviewed and approved
- Performance targets met
