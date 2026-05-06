# SI Extraction Using SpecKit

This project implements a PDF metadata extraction pipeline using a React + TypeScript frontend and a FastAPI backend. Its goal is to extract academic metadata from PDF files, including title, DOI, abstract, keywords, publication date, journal, authors, and affiliations.

## Project Structure

- `backend/`
  - FastAPI service for PDF upload, extraction job management, and metadata extraction
  - `src/services/rag_extractor.py` handles LLM-assisted and heuristic fallback metadata extraction
  - `src/services/pdf_processor.py` extracts PDF text and embedded PDF metadata
  - tests for integration and unit validation
- `frontend/`
  - Vite + React application for uploading PDFs and displaying extracted metadata
  - `src/components/` contains UI panels and upload controls
- `docs/`
  - development and setup documentation

## How to Run

### Backend

1. Create and activate a Python virtual environment
2. Install dependencies:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```
3. Start the backend server:
   ```bash
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the frontend dev server:
   ```bash
   npm run dev
   ```

## Notes

- The backend currently supports extraction using a local Ollama LLM service if available.
- A heuristic fallback parser is used when the LLM is unavailable.
- A `SI_Extraction_UsingSpecKit/` nested directory appears in the workspace but is not part of the main Git working tree.
