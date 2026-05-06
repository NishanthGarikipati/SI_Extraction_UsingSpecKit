/**
 * Frontend TypeScript type definitions for data models
 * Based on data-model.md entity definitions
 */

// Author information
export interface Author {
  id: string;
  name: string;
  email?: string;
  orcid?: string;
  affiliation_ids: string[];
}

// Institution/affiliation information
export interface Affiliation {
  id: string;
  institution: string;
  department?: string;
  city?: string;
  country?: string;
  postal_code?: string;
}

// Confidence scores for extracted fields
export interface ConfidenceScores {
  title?: number;
  doi?: number;
  authors?: number;
  abstract?: number;
  keywords?: number;
  publication_date?: number;
  journal?: number;
  affiliations?: number;
}

// Extracted metadata from PDF
export interface ExtractedMetadata {
  id: string;
  extraction_job_id: string;
  title: string;
  doi?: string;
  abstract?: string;
  keywords: string[];
  publication_date?: string;
  journal?: string;
  authors: Author[];
  affiliations: Affiliation[];
  confidence_scores: ConfidenceScores;
  overall_confidence: number;
  extraction_timestamp: string;
  source_file?: string;
}

// PDF document information
export interface PDFDocument {
  id: string;
  filename: string;
  file_size: number;
  upload_timestamp: string;
  page_count?: number;
  text_content?: string;
  storage_location: string;
  validation_status: 'valid' | 'invalid';
  validation_error?: string;
}

// Extraction job tracking
export interface ExtractionJob {
  id: string;
  pdf_document_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout';
  start_time?: string;
  end_time?: string;
  elapsed_time_ms: number;
  error?: string;
  llm_model: string;
  retry_count: number;
  raw_llm_output?: string;
}

// Exported files
export interface ExportFile {
  format: 'json' | 'xml' | 'toon';
  filename: string;
  mime_type: string;
  file_size: number;
  download_url: string;
}

export interface ExportedFiles {
  id: string;
  metadata_id: string;
  generated_timestamp: string;
  files: Record<'json' | 'xml' | 'toon', ExportFile>;
}

// Application state
export interface PDFState {
  document: PDFDocument | null;
  currentPage: number;
  isLoading: boolean;
  error: string | null;
}

export interface ExtractionState {
  job: ExtractionJob | null;
  metadata: ExtractedMetadata | null;
  isLoading: boolean;
  error: string | null;
}

export interface ExportState {
  files: ExportedFiles | null;
  isLoading: boolean;
  error: string | null;
}

export interface UIState {
  activeTab: 'metadata' | 'export';
  editingFieldId: string | null;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  timestamp: number;
  duration?: number;
}

export interface AppState {
  pdf: PDFState;
  extraction: ExtractionState;
  export: ExportState;
  ui: UIState;
}
