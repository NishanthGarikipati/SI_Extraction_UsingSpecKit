/**
 * Main Application Component
 * Split-panel layout: metadata on left, PDF on right
 */
import { useEffect } from 'react'
import { UploadArea } from '../components/UploadArea'
import { PDFViewer } from '../components/PDFViewer'
import { MetadataPanel } from '../components/MetadataPanel'
import { useAppStore } from '../hooks/useAppState'
import { apiClient } from '../services/api'
import '../styles/index.css'

function App() {
  const {
    pdf,
    extraction,
    ui,
    addNotification,
    setPDFError,
    setExtractionLoading,
    setExtractionError,
    setMetadata,
  } = useAppStore()

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        await apiClient.checkHealth()
        console.log('API is healthy')
      } catch (error) {
        addNotification({
          type: 'error',
          message: 'Cannot connect to API server. Please ensure backend is running.',
          duration: Infinity,
        })
      }
    }

    checkHealth()
  }, [])

  const handleUploadComplete = async (jobId: string) => {
    try {
      setExtractionLoading(true)
      setExtractionError(null)

      // Poll for extraction completion
      const metadata = await apiClient.pollExtractionUntilComplete(jobId)
      setMetadata(metadata)

      addNotification({
        type: 'success',
        message: 'Metadata extraction completed successfully!',
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Extraction failed'
      setExtractionError(message)
      addNotification({
        type: 'error',
        message: `Extraction error: ${message}`,
      })
    } finally {
      setExtractionLoading(false)
    }
  }

  return (
    <div className="flex h-screen w-screen bg-white">
      {/* Left Panel: Metadata */}
      <div className="split-panel split-panel-left w-1/3 border-r border-gray-200">
        {extraction.metadata ? (
          <MetadataPanel metadata={extraction.metadata} />
        ) : (
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Extracted Metadata</h2>
            <p className="text-gray-500">
              Upload a PDF and complete the extraction to see metadata here.
            </p>
          </div>
        )}
      </div>

      {/* Right Panel: PDF Viewer */}
      <div className="split-panel w-2/3">
        {!pdf.document ? (
          <UploadArea
            onUploadComplete={handleUploadComplete}
            onError={(error: string) => {
              setPDFError(error)
              addNotification({
                type: 'error',
                message: error,
              })
            }}
          />
        ) : (
          <div className="flex flex-col h-full">
            <PDFViewer
              pdfUrl={pdf.document.storage_location}
              className="flex-1"
            />
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-sm">
              <p className="text-gray-600">
                📄 {pdf.document.filename} ({(pdf.document.file_size / 1024 / 1024).toFixed(2)}MB)
              </p>
            </div>
          </div>
        )}

        {/* Error Display */}
        {pdf.error && (
          <div className="absolute top-4 right-4 max-w-md error-message">
            <p className="font-semibold">Upload Error</p>
            <p className="text-sm">{pdf.error}</p>
          </div>
        )}
      </div>

      {/* Notifications */}
      <div className="fixed bottom-4 right-4 space-y-2 max-w-md">
        {ui.notifications.map((notif: any) => (
          <div
            key={notif.id}
            className={`p-4 rounded-lg text-white animate-fade-in ${
              notif.type === 'success' ? 'bg-green-500' :
              notif.type === 'error' ? 'bg-red-500' :
              notif.type === 'warning' ? 'bg-yellow-500' :
              'bg-blue-500'
            }`}
          >
            <p className="font-medium">{notif.message}</p>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {(extraction.isLoading) && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 text-center">
            <div className="loading-spinner w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full mx-auto mb-4"></div>
            <p className="text-lg font-semibold text-gray-900">
              Extracting metadata...
            </p>
            <p className="text-sm text-gray-500 mt-2">
              This may take up to 30 seconds
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
