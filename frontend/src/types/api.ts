/**
 * API request and response type definitions
 * Based on contracts/api-specification.md
 */

import type { ExtractedMetadata } from './index'

// ============ Health Check ============

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
  timestamp: string;
  services?: {
    ollama?: 'connected' | 'disconnected';
    pdf_processor?: 'ready' | 'not_ready';
  };
}

// ============ PDF Upload / Extraction ============

export interface ExtractRequest {
  file: File;
}

export interface ExtractResponse {
  job_id: string;
  status: 'pending';
  pdf_id: string;
  poll_interval_ms: number;
}

// ============ Extraction Status ============

export interface StatusRequest {
  job_id: string;
}

export interface StatusResponse {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'timeout';
  elapsed_time_ms: number;
  estimated_remaining_ms?: number;
  metadata?: ExtractedMetadata;
  error?: string;
  retry_available: boolean;
  retry_count: number;
}

// ============ Export ============

export interface ExportRequest {
  metadata_id: string;
  formats: ('json' | 'xml' | 'toon')[];
  include_confidence?: boolean;
  filename_prefix?: string;
}

export interface ExportResponse {
  export_id: string;
  files: Record<'json' | 'xml' | 'toon', {
    format: string;
    filename: string;
    mime_type: string;
    file_size: number;
    download_url: string;
  }>;
}

// ============ Download ============

export interface DownloadRequest {
  export_id: string;
  format: 'json' | 'xml' | 'toon';
}

// ============ Error Responses ============

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
  request_id?: string;
}

// ============ API Client Configuration ============

export interface APIConfig {
  baseURL: string;
  timeout: number;
  retries: number;
}

// ============ Polling Options ============

export interface PollOptions {
  interval_ms: number;
  max_attempts: number;
  backoff_multiplier: number;
}
