/**
 * API client service for communicating with backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios'
import type { 
  ExtractResponse, 
  StatusResponse, 
  ExportResponse, 
  ErrorResponse,
  HealthCheckResponse 
} from '../types/api'
import type { ExtractedMetadata } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
const API_TIMEOUT = 30000 // 30 seconds

class APIClient {
  private client: AxiosInstance
  private correlationId: string

  constructor() {
    this.correlationId = this.generateCorrelationId()
    
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
        'X-Correlation-ID': this.correlationId,
      },
    })

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      response => response,
      error => this.handleError(error)
    )
  }

  private generateCorrelationId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  private handleError(error: AxiosError): Promise<never> {
    const errorResponse = error.response?.data as ErrorResponse | undefined
    
    console.error('API Error:', {
      status: error.response?.status,
      message: errorResponse?.message || error.message,
      correlationId: this.correlationId,
    })

    return Promise.reject({
      status: error.response?.status || 500,
      message: errorResponse?.message || error.message,
      details: errorResponse?.details,
      correlationId: this.correlationId,
    })
  }

  /**
   * Check API and service health
   */
  async checkHealth(): Promise<HealthCheckResponse> {
    try {
      const response = await this.client.get<HealthCheckResponse>('/health')
      return response.data
    } catch (error) {
      throw new Error('Failed to connect to API: ' + String(error))
    }
  }

  /**
   * Upload PDF file and start extraction
   */
  async uploadPDF(file: File): Promise<ExtractResponse> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await this.client.post<ExtractResponse>(
        '/extract',
        formData,
        {
          headers: {
            'Content-Type': undefined,
          },
        }
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 413) {
          throw new Error('File is too large. Maximum size is 50MB.')
        }
        if (error.response?.status === 400) {
          throw new Error('Invalid file format. Please upload a PDF file.')
        }
      }
      throw error
    }
  }

  /**
   * Poll extraction job status
   */
  async getExtractionStatus(jobId: string): Promise<StatusResponse> {
    try {
      const response = await this.client.get<StatusResponse>(
        `/extract/${jobId}`
      )
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        throw new Error(`Extraction job ${jobId} not found`)
      }
      throw error
    }
  }

  /**
   * Poll with automatic retry until completion or timeout
   */
  async pollExtractionUntilComplete(
    jobId: string,
    timeoutMs: number = 300000, // 5 minutes default
    intervalMs: number = 1000   // Poll every second
  ): Promise<ExtractedMetadata> {
    const startTime = Date.now()

    return new Promise((resolve, reject) => {
      const pollTimer = setInterval(async () => {
        try {
          const status = await this.getExtractionStatus(jobId)

          if (status.status === 'completed' && status.metadata) {
            clearInterval(pollTimer)
            resolve(status.metadata)
            return
          }

          if (status.status === 'failed') {
            clearInterval(pollTimer)
            reject(new Error(`Extraction failed: ${status.error}`))
            return
          }

          if (status.status === 'timeout') {
            clearInterval(pollTimer)
            reject(new Error('Extraction timed out'))
            return
          }

          // Check overall timeout
          if (Date.now() - startTime > timeoutMs) {
            clearInterval(pollTimer)
            reject(new Error('Polling timeout exceeded'))
          }
        } catch (error) {
          clearInterval(pollTimer)
          reject(error)
        }
      }, intervalMs)
    })
  }

  /**
   * Generate export files for metadata
   */
  async generateExport(
    metadataId: string,
    formats: ('json' | 'xml' | 'toon')[] = ['json'],
    options?: {
      include_confidence?: boolean
      filename_prefix?: string
    }
  ): Promise<ExportResponse> {
    try {
      const response = await this.client.post<ExportResponse>(
        '/export',
        {
          metadata_id: metadataId,
          formats,
          ...options,
        }
      )
      return response.data
    } catch (error) {
      const errorMessage = axios.isAxiosError(error)
        ? error.response?.data?.message ?? error.message
        : error && typeof error === 'object'
        ? (error as any).message ?? JSON.stringify(error)
        : String(error)
      throw new Error('Failed to generate export files: ' + errorMessage)
    }
  }

  /**
   * Download exported file
   */
  async downloadFile(exportId: string, format: 'json' | 'xml' | 'toon'): Promise<Blob> {
    try {
      const response = await this.client.get<Blob>(
        `/download/${exportId}/${format}`,
        { responseType: 'blob' }
      )
      return response.data
    } catch (error) {
      const errorMessage = axios.isAxiosError(error)
        ? error.response?.data?.message ?? error.message
        : error && typeof error === 'object'
        ? (error as any).message ?? JSON.stringify(error)
        : String(error)
      throw new Error(`Failed to download ${format} file: ${errorMessage}`)
    }
  }

  /**
   * Trigger browser download for a blob
   */
  triggerBrowserDownload(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'
    
    document.body.appendChild(link)
    link.click()
    
    // Cleanup
    setTimeout(() => {
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
    }, 100)
  }

  /**
   * Update correlation ID for next requests
   */
  setCorrelationId(id: string): void {
    this.correlationId = id
    this.client.defaults.headers['X-Correlation-ID'] = id
  }
}

// Export singleton instance
export const apiClient = new APIClient()
export default apiClient
