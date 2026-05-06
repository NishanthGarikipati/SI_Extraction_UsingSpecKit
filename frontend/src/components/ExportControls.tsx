/**
 * Export controls component
 */
import React from 'react'
import { useAppStore } from '../hooks/useAppState'
import { apiClient } from '../services/api'

interface ExportControlsProps {
  metadata: any
}

export const ExportControls: React.FC<ExportControlsProps> = ({ metadata }) => {
  const { addNotification } = useAppStore()
  const [isExporting, setIsExporting] = React.useState(false)
  const [selectedFormats, setSelectedFormats] = React.useState<string[]>(['json'])
  const [includeConfidence, setIncludeConfidence] = React.useState(true)

  const handleFormatToggle = (format: string) => {
    setSelectedFormats(prev =>
      prev.includes(format)
        ? prev.filter(f => f !== format)
        : [...prev, format]
    )
  }

  const handleExportClick = async () => {
    if (!metadata || selectedFormats.length === 0) {
      addNotification({ type: 'error', message: 'Please select at least one format' })
      return
    }

    setIsExporting(true)
    try {
      const response = await apiClient.generateExport(
        metadata.id,
        selectedFormats as any[],
        { include_confidence: includeConfidence }
      )

      // Download each file
      for (const [format, filenameValue] of Object.entries(response.files)) {
        const filename = String(filenameValue)
        const blob = await apiClient.downloadFile(response.export_id, format as any)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }

      addNotification({ type: 'success', message: 'Files downloaded successfully' })
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : error && typeof error === 'object'
          ? JSON.stringify(error)
          : String(error)

      addNotification({ type: 'error', message: `Export failed: ${message}` })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="border-t border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Metadata</h3>

      {/* Format Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Export Formats
        </label>
        <div className="space-y-2">
          {['json', 'xml', 'toon'].map(format => (
            <label key={format} className="flex items-center">
              <input
                type="checkbox"
                checked={selectedFormats.includes(format)}
                onChange={() => handleFormatToggle(format)}
                className="rounded border-gray-300"
              />
              <span className="ml-2 text-sm text-gray-700">
                {format.toUpperCase()}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Confidence Scores */}
      <div className="mb-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={includeConfidence}
            onChange={e => setIncludeConfidence(e.target.checked)}
            className="rounded border-gray-300"
          />
          <span className="ml-2 text-sm text-gray-700">
            Include confidence scores
          </span>
        </label>
      </div>

      {/* Export Button */}
      <button
        onClick={handleExportClick}
        disabled={isExporting || selectedFormats.length === 0}
        className="btn btn-primary"
      >
        {isExporting ? 'Exporting...' : 'Export Files'}
      </button>
    </div>
  )
}
