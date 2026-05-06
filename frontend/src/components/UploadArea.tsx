/**
 * PDF Upload Area Component
 * Handles drag-drop and file selection
 */
import React, { useRef } from 'react'
import { useAppStore } from '../hooks/useAppState'
import { apiClient } from '../services/api'

interface UploadAreaProps {
  onUploadStart?: () => void
  onUploadComplete?: (jobId: string) => void
  onError?: (error: string) => void
}

export const UploadArea: React.FC<UploadAreaProps> = ({
  onUploadStart,
  onUploadComplete,
  onError,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isDragging, setIsDragging] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  
  const { setPDFLoading, setPDFError } = useAppStore()

  const handleFileSelect = async (file: File) => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      const error = 'Please select a PDF file'
      setPDFError(error)
      onError?.(error)
      return
    }

    try {
      setIsLoading(true)
      onUploadStart?.()
      setPDFLoading(true)
      
      const response = await apiClient.uploadPDF(file)
      setPDFError(null)
      onUploadComplete?.(response.job_id)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Upload failed'
      setPDFError(message)
      onError?.(message)
    } finally {
      setIsLoading(false)
      setPDFLoading(false)
    }
  }

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  return (
    <div className="w-full h-full flex items-center justify-center p-8">
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`w-full max-w-md p-8 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400 bg-gray-50'
        } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
        onClick={() => !isLoading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          disabled={isLoading}
          className="hidden"
        />

        <div className="space-y-4">
          <div className="text-4xl">📄</div>
          
          {isLoading ? (
            <>
              <div className="text-lg font-semibold text-gray-700">
                Uploading...
              </div>
              <div className="flex justify-center">
                <div className="loading-spinner w-6 h-6 border-2 border-blue-200 border-t-blue-500 rounded-full"></div>
              </div>
            </>
          ) : (
            <>
              <div>
                <p className="text-lg font-semibold text-gray-700">
                  Drag & drop your PDF here
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  or click to browse
                </p>
              </div>
              <p className="text-xs text-gray-400">
                Maximum file size: 50MB
              </p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
