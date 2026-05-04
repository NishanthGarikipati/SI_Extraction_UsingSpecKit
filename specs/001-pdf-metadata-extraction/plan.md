# Implementation Plan: PDF Metadata Extraction UI

**Branch**: `001-pdf-rag-metadata-extractor` | **Date**: 2026-05-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-pdf-metadata-extraction/spec.md`

---

## Summary

Build a split-panel React/TypeScript web application that enables researchers to upload scientific PDFs, extract structured metadata using a local LLaMA 2/Ollama RAG model, review and edit extracted fields, and export results as JSON, XML, and TOON formats. The application features a two-column layout: PDF viewer on the right, extracted metadata list on the left with full edit capability. Metadata extraction focuses on core academic fields: title, DOI, authors, affiliations, keywords, abstract, publication date, and journal name. All data is generated and exported client-side or via API calls to a Python backend service.

---

## Technical Context

**Frontend Language/Version**: TypeScript 5.0+, React 18.2+  
**Frontend Framework**: React with TypeScript, Vite (build tool)  
**Frontend UI Library**: React PDF Viewer (react-pdf or pdfjs-dist), Tailwind CSS for styling  
**State Management**: React Context API or Zustand for lightweight state management  
**Form/Input Handling**: React Hook Form for metadata editing, input validation  

**Backend Language/Version**: Python 3.10+  
**Backend Framework**: FastAPI (async REST API)  
**RAG/ML Model**: LLaMA 2 via Ollama (local, self-hosted)  
**PDF Processing**: PyPDF2 or pdfplumber for text extraction, langchain for RAG pipeline  
**File Output**: json, xml, toon format generation using native Python libraries  

**Storage**: File system only (no database required for v1)  
**Testing Frontend**: Vitest + React Testing Library (unit), Playwright (E2E)  
**Testing Backend**: pytest + pytest-asyncio (unit + integration)  
**Target Platform**: Desktop web browsers (Chrome, Firefox, Safari, Edge); Desktop-only v1  
**Project Type**: Full-stack web application (SPA + REST API backend)  

**Performance Goals**:
- Page load (FCP): < 1.5s | LCP: < 2.5s
- PDF upload & display: < 3s
- Metadata extraction: < 30s (typical 5-20 page PDF)
- Export generation: < 5s
- API response (p95): < 500ms

**Constraints**:
- File size limit: 50MB PDFs
- Extraction accuracy target: 85%+
- Client-side bundle (main JS): < 200KB gzipped
- Extraction timeout: 30s hard limit
- No authentication/multi-user for v1

**Scale/Scope**:
- 4 screens/views (upload, extraction in progress, metadata review, export ready)
- 8 metadata fields (extensible to 10+)
- 3 export formats (JSON, XML, TOON)
- Single-document workflow (one PDF at a time)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality (I. Code Quality - Non-Negotiable)
**Status**: PASSES  
**Justification**: Feature design includes:
- Clear module separation (frontend/backend, components/services)
- Single Responsibility: PDF handling, metadata extraction, UI display are separate concerns
- Type safety via TypeScript on frontend, type hints on Python backend
- Linting/formatting will be enforced pre-commit
- Code review gates defined in tasks phase

### Testing Standards (II. Testing Standards - Non-Negotiable)
**Status**: PASSES with requirement for task definition  
**Justification**: Feature will include:
- Unit tests for all utility functions, API handlers, React components (80%+ coverage target)
- Integration tests for metadata extraction pipeline and API endpoints
- E2E tests for critical user journey: upload → extract → review → export
- Performance benchmarks for extraction and rendering times
- **ACTION**: Testing strategy details will be defined in tasks.md phase

### UX Consistency (III. User Experience Consistency)
**Status**: PASSES with design validation required  
**Justification**: Feature includes:
- Consistent split-panel layout with clear visual hierarchy
- WCAG 2.1 AA compliance requirements (keyboard navigation, contrast, screen reader support)
- Responsive design (desktop-first, 1366x768 minimum)
- Clear loading states, error messages with actionable guidance
- Design system adherence via Tailwind CSS utility classes
- **ACTION**: Mockups should be validated with target users before implementation

### Performance Requirements (IV. Performance Requirements)
**Status**: PASSES with monitoring plan required  
**Justification**: Feature meets all critical targets:
- FCP/LCP targets: Vite + code splitting can achieve < 1.5s FCP for typical SPA
- API response: FastAPI async handles < 500ms target for extraction coordination
- Bundle size: React + UI libraries typically < 200KB gzipped with proper tree-shaking
- PDF rendering: react-pdf optimized for paginated display
- **ACTION**: Performance monitoring and benchmarking will be implemented in implementation phase

**GATE RESULT**: ✅ PASSES - All constitution principles are satisfied or accommodated in design.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-pdf-metadata-extraction/
├── plan.md                          # This file (planning output)
├── research.md                      # Phase 0: Research & technical decisions
├── data-model.md                    # Phase 1: Data structures & entities
├── contracts/                       # Phase 1: API contracts
│   ├── extract-metadata-api.md      # Backend RAG extraction API
│   ├── export-formats.md            # Export file format specifications
│   └── metadata-schema.json         # Shared metadata structure
├── quickstart.md                    # Phase 1: Setup & first run guide
├── checklists/
│   └── requirements.md              # Specification quality checklist
└── tasks.md                         # Phase 2 output (generated by /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/                           # React/TypeScript SPA
├── src/
│   ├── components/
│   │   ├── PDFViewer.tsx           # PDF display component
│   │   ├── MetadataPanel.tsx       # Left panel: metadata list
│   │   ├── MetadataField.tsx       # Editable metadata field
│   │   ├── UploadArea.tsx          # PDF upload UI
│   │   ├── ExtractionProgress.tsx  # Extraction loading state
│   │   └── ExportPanel.tsx         # Export options & downloads
│   ├── pages/
│   │   └── App.tsx                 # Main application page
│   ├── services/
│   │   ├── api.ts                  # API client (extraction, export)
│   │   ├── fileExport.ts           # Client-side file generation
│   │   └── pdfStorage.ts           # PDF storage (memory + local)
│   ├── types/
│   │   └── index.ts                # TypeScript interfaces (Metadata, ExtractionJob, etc.)
│   ├── hooks/
│   │   ├── useExtraction.ts        # Metadata extraction hook
│   │   ├── useFileUpload.ts        # PDF upload & validation hook
│   │   └── useMetadataState.ts     # Metadata state management
│   ├── styles/
│   │   └── index.css               # Tailwind CSS configuration & globals
│   └── main.tsx                    # React entry point
├── tests/
│   ├── unit/                       # Unit tests (Vitest)
│   ├── integration/                # Integration tests
│   └── e2e/                        # End-to-end tests (Playwright)
├── package.json
├── vite.config.ts
└── tailwind.config.ts

backend/                            # Python FastAPI service
├── src/
│   ├── main.py                     # FastAPI app entry point
│   ├── models/
│   │   ├── metadata.py             # Pydantic models for API
│   │   └── extraction_result.py    # ExtractionResult model
│   ├── services/
│   │   ├── pdf_processor.py        # PDF text extraction
│   │   ├── rag_extractor.py        # LLaMA 2/Ollama RAG pipeline
│   │   ├── metadata_parser.py      # Parse RAG output to structured data
│   │   └── export_generator.py     # JSON, XML, TOON file generation
│   ├── api/
│   │   ├── routes.py               # API endpoints
│   │   ├── dependencies.py         # Dependency injection
│   │   └── health.py               # Health check endpoint
│   ├── config.py                   # Configuration (Ollama host, model, etc.)
│   ├── utils/
│   │   ├── logging.py              # Structured logging
│   │   └── validators.py           # Input validation
│   └── prompts/
│       └── extraction_prompt.txt   # LLM prompt template for metadata extraction
├── tests/
│   ├── unit/                       # Unit tests (pytest)
│   ├── integration/                # Integration tests (pytest)
│   └── fixtures/                   # Test PDFs, mock responses
├── requirements.txt
├── pyproject.toml
└── Dockerfile (optional)

docs/                               # Deployment & operational docs
├── DEPLOYMENT.md
├── ARCHITECTURE.md
└── DEV_SETUP.md
```

**Structure Decision**: Full-stack separation with dedicated frontend (React/Vite SPA) and backend (Python/FastAPI) directories. This allows:
- Independent deployment and scaling
- Clear API contract between layers
- Separate testing strategies (frontend E2E, backend unit+integration)
- Easy containerization of backend (Ollama + FastAPI)
- Flexible frontend hosting (static CDN, SPA platform, or self-hosted)

---

## Complexity Tracking

**Gate Status**: ✅ PASSES - No constitution violations requiring justification. All principles are aligned with feature design.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
