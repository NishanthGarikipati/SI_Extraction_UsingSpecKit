/**
 * PDF Viewer Component
 * Displays PDF pages using react-pdf
 */
import React, { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

// Set PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

interface PDFViewerProps {
  pdfUrl?: string | null
  className?: string
  onPageChange?: (page: number) => void
}

export const PDFViewer: React.FC<PDFViewerProps> = ({
  pdfUrl,
  className = '',
  onPageChange,
}) => {
  const [numPages, setNumPages] = useState<number | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setIsLoading(false)
    setError(null)
  }

  const handleDocumentLoadError = (error: Error) => {
    console.error('PDF load error:', error)
    setError('Failed to load PDF')
    setIsLoading(false)
  }

  const goToPage = (page: number) => {
    if (numPages && page >= 1 && page <= numPages) {
      setCurrentPage(page)
      onPageChange?.(page)
    }
  }

  const handlePrevious = () => goToPage(currentPage - 1)
  const handleNext = () => goToPage(currentPage + 1)

  if (!pdfUrl) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <p className="text-gray-500">No PDF loaded</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="error-message">
          <p className="font-semibold">Error loading PDF</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full bg-gray-50 ${className}`}>
      {/* Controls */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1 || isLoading}
          className="btn btn-secondary disabled:btn-disabled"
        >
          ← Previous
        </button>

        <div className="flex items-center gap-2">
          <input
            type="number"
            min="1"
            max={numPages || 1}
            value={currentPage}
            onChange={(e) => goToPage(parseInt(e.target.value))}
            disabled={isLoading}
            className="form-input w-16 text-center py-1"
          />
          <span className="text-sm text-gray-600">
            / {numPages || '?'} pages
          </span>
        </div>

        <button
          onClick={handleNext}
          disabled={currentPage === numPages || isLoading}
          className="btn btn-secondary disabled:btn-disabled"
        >
          Next →
        </button>
      </div>

      {/* PDF Viewer */}
      <div className="flex-1 overflow-auto flex items-center justify-center">
        {isLoading && (
          <div className="flex flex-col items-center gap-2">
            <div className="loading-spinner w-8 h-8 border-4 border-blue-200 border-t-blue-500 rounded-full"></div>
            <p className="text-gray-500">Loading PDF...</p>
          </div>
        )}

        {!isLoading && pdfUrl && (
          <Document
            file={pdfUrl}
            onLoadSuccess={handleDocumentLoadSuccess}
            onLoadError={handleDocumentLoadError}
            onLoadStart={() => setIsLoading(true)}
            loading={null}
          >
            <Page
              pageNumber={currentPage}
              renderTextLayer
              renderAnnotationLayer
              scale={1.5}
              className="pdf-page"
            />
          </Document>
        )}
      </div>

      {/* Page Info Footer */}
      {numPages && (
        <div className="px-4 py-2 bg-white border-t border-gray-200 text-sm text-gray-600 text-center">
          Page {currentPage} of {numPages}
        </div>
      )}
    </div>
  )
}
