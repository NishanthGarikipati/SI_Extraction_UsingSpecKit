/**
 * Global application state management using Zustand
 */
import { create } from 'zustand'
import type {
  AppState,
  PDFDocument,
  ExtractedMetadata,
  Notification,
  Author,
  Affiliation,
  ExportedFiles,
} from '../types'

interface AppStore extends AppState {
  // PDF actions
  setPDFDocument: (doc: PDFDocument | null) => void
  setCurrentPage: (page: number) => void
  setPDFLoading: (loading: boolean) => void
  setPDFError: (error: string | null) => void
  
  // Extraction actions
  setExtractionJob: (job: any | null) => void
  setMetadata: (metadata: ExtractedMetadata | null) => void
  setExtractionLoading: (loading: boolean) => void
  setExtractionError: (error: string | null) => void
  
  // Metadata editing
  updateMetadataField: <K extends keyof ExtractedMetadata>(field: K, value: ExtractedMetadata[K]) => void
  updateAuthor: (authorId: string, author: Author) => void
  updateAffiliation: (affId: string, affiliation: Affiliation) => void
  
  // Export actions
  setExportedFiles: (files: ExportedFiles | null) => void
  setExportLoading: (loading: boolean) => void
  setExportError: (error: string | null) => void
  
  // UI actions
  setActiveTab: (tab: 'metadata' | 'export') => void
  setEditingFieldId: (fieldId: string | null) => void
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  
  // Reset
  reset: () => void
}

const initialState: AppState = {
  pdf: {
    document: null,
    currentPage: 1,
    isLoading: false,
    error: null,
  },
  extraction: {
    job: null,
    metadata: null,
    isLoading: false,
    error: null,
  },
  export: {
    files: null,
    isLoading: false,
    error: null,
  },
  ui: {
    activeTab: 'metadata',
    editingFieldId: null,
    notifications: [],
  },
}

export const useAppStore = create<AppStore>((set, get) => ({
  ...initialState,

  // PDF actions
  setPDFDocument: (doc) =>
    set((state) => ({
      pdf: { ...state.pdf, document: doc },
    })),

  setCurrentPage: (page) =>
    set((state) => ({
      pdf: { ...state.pdf, currentPage: page },
    })),

  setPDFLoading: (loading) =>
    set((state) => ({
      pdf: { ...state.pdf, isLoading: loading },
    })),

  setPDFError: (error) =>
    set((state) => ({
      pdf: { ...state.pdf, error },
    })),

  // Extraction actions
  setExtractionJob: (job) =>
    set((state) => ({
      extraction: { ...state.extraction, job },
    })),

  setMetadata: (metadata) =>
    set((state) => ({
      extraction: { ...state.extraction, metadata },
    })),

  setExtractionLoading: (loading) =>
    set((state) => ({
      extraction: { ...state.extraction, isLoading: loading },
    })),

  setExtractionError: (error) =>
    set((state) => ({
      extraction: { ...state.extraction, error },
    })),

  // Metadata editing
  updateMetadataField: (field, value) =>
    set((state) => {
      if (!state.extraction.metadata) return state
      return {
        extraction: {
          ...state.extraction,
          metadata: {
            ...state.extraction.metadata,
            [field]: value,
          },
        },
      }
    }),

  updateAuthor: (authorId, author) =>
    set((state) => {
      if (!state.extraction.metadata) return state
      return {
        extraction: {
          ...state.extraction,
          metadata: {
            ...state.extraction.metadata,
            authors: state.extraction.metadata.authors.map((a) =>
              a.id === authorId ? author : a
            ),
          },
        },
      }
    }),

  updateAffiliation: (affId, affiliation) =>
    set((state) => {
      if (!state.extraction.metadata) return state
      return {
        extraction: {
          ...state.extraction,
          metadata: {
            ...state.extraction.metadata,
            affiliations: state.extraction.metadata.affiliations.map((a) =>
              a.id === affId ? affiliation : a
            ),
          },
        },
      }
    }),

  // Export actions
  setExportedFiles: (files) =>
    set((state) => ({
      export: { ...state.export, files },
    })),

  setExportLoading: (loading) =>
    set((state) => ({
      export: { ...state.export, isLoading: loading },
    })),

  setExportError: (error) =>
    set((state) => ({
      export: { ...state.export, error },
    })),

  // UI actions
  setActiveTab: (tab) =>
    set((state) => ({
      ui: { ...state.ui, activeTab: tab },
    })),

  setEditingFieldId: (fieldId) =>
    set((state) => ({
      ui: { ...state.ui, editingFieldId: fieldId },
    })),

  addNotification: (notification) => {
    const id = `notif-${Date.now()}-${Math.random()}`
    const notif: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
    }

    set((state) => ({
      ui: {
        ...state.ui,
        notifications: [...state.ui.notifications, notif],
      },
    }))

    // Auto-remove after duration
    if (notification.duration !== Infinity) {
      setTimeout(() => {
        get().removeNotification(id)
      }, notification.duration || 5000)
    }
  },

  removeNotification: (id) =>
    set((state) => ({
      ui: {
        ...state.ui,
        notifications: state.ui.notifications.filter((n) => n.id !== id),
      },
    })),

  // Reset
  reset: () => set(initialState),
}))
