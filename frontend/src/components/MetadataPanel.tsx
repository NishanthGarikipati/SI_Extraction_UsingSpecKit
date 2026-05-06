/**
 * Metadata Display and Editing Panel Component
 */
import React from 'react'
import type { ExtractedMetadata } from '../types'
import { useAppStore } from '../hooks/useAppState'
import { ExportControls } from './ExportControls'

interface MetadataPanelProps {
  metadata: ExtractedMetadata
}

export const MetadataPanel: React.FC<MetadataPanelProps> = ({ metadata }) => {
  const { updateMetadataField } = useAppStore()
  const [localEdits, setLocalEdits] = React.useState<Record<string, any>>({})

  const handleFieldEdit = (field: keyof ExtractedMetadata, value: any) => {
    setLocalEdits({ ...localEdits, [field]: value })
    updateMetadataField(field, value)
  }

  return (
    <div className="h-full overflow-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b border-gray-200 p-6 z-10">
        <h2 className="text-2xl font-bold text-gray-900">Extracted Metadata</h2>
        <p className="text-sm text-gray-500 mt-1">
          Overall Confidence: {Math.round(metadata.overall_confidence * 100)}%
        </p>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Basic Information Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Basic Information
          </h3>
          <div className="space-y-4">
            {/* Title */}
            <div className="metadata-field">
              <label className="form-label">Title</label>
              <input
                type="text"
                value={metadata.title}
                onChange={(e) => handleFieldEdit('title', e.target.value)}
                className="form-input"
                placeholder="Article title"
              />
              {metadata.confidence_scores.title && (
                <p className="text-xs text-gray-500 mt-1">
                  Confidence: {Math.round(metadata.confidence_scores.title * 100)}%
                </p>
              )}
            </div>

            {/* DOI */}
            <div className="metadata-field">
              <label className="form-label">DOI</label>
              <input
                type="text"
                value={metadata.doi || ''}
                onChange={(e) => handleFieldEdit('doi', e.target.value || undefined)}
                className="form-input"
                placeholder="10.xxxx/xxxx"
              />
            </div>

            {/* Publication Date */}
            <div className="metadata-field">
              <label className="form-label">Publication Date</label>
              <input
                type="date"
                value={metadata.publication_date?.split('T')[0] || ''}
                onChange={(e) => handleFieldEdit('publication_date', e.target.value || undefined)}
                className="form-input"
              />
            </div>

            {/* Journal */}
            <div className="metadata-field">
              <label className="form-label">Journal</label>
              <input
                type="text"
                value={metadata.journal || ''}
                onChange={(e) => handleFieldEdit('journal', e.target.value || undefined)}
                className="form-input"
                placeholder="Journal name"
              />
            </div>
          </div>
        </div>

        {/* Abstract Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Abstract</h3>
          <textarea
            value={metadata.abstract || ''}
            onChange={(e) => handleFieldEdit('abstract', e.target.value || undefined)}
            rows={4}
            className="form-input"
            placeholder="Abstract text..."
          />
        </div>

        {/* Keywords Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {metadata.keywords.map((keyword, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>

        {/* Authors Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Authors ({metadata.authors.length})
          </h3>
          <div className="space-y-3">
            {metadata.authors.map((author) => (
              <div key={author.id} className="metadata-field">
                <p className="font-medium text-gray-900">{author.name}</p>
                {author.email && <p className="text-sm text-gray-600">{author.email}</p>}
                {author.orcid && <p className="text-sm text-gray-600">ORCID: {author.orcid}</p>}
                {author.affiliation_ids.length > 0 && (
                  <p className="text-xs text-gray-500 mt-2">
                    Affiliations: {author.affiliation_ids.join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Affiliations Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Affiliations ({metadata.affiliations.length})
          </h3>
          <div className="space-y-3">
            {metadata.affiliations.map((aff) => (
              <div key={aff.id} className="metadata-field">
                <p className="font-medium text-gray-900">{aff.institution}</p>
                {aff.department && <p className="text-sm text-gray-600">{aff.department}</p>}
                {(aff.city || aff.country) && (
                  <p className="text-sm text-gray-600">
                    {[aff.city, aff.country].filter(Boolean).join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Metadata Info */}
        <div className="p-4 bg-gray-50 rounded-lg text-xs text-gray-600">
          <p>Extracted: {new Date(metadata.extraction_timestamp).toLocaleString()}</p>
          {metadata.source_file && <p>Source: {metadata.source_file}</p>}
        </div>

        {/* Export Controls */}
        <ExportControls metadata={metadata} />
      </div>
    </div>
  )
}
