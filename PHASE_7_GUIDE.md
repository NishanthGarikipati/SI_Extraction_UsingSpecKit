# Implementation Guide - Phase 7-9 Continuation

## Overview
This guide helps developers continue from Phase 6 completion (export/download) into Phase 7-9 (UI polish, testing, production).

## Current State (End of Phase 6)
- ✅ All core features implemented
- ✅ Backend API fully functional
- ✅ Frontend React components created
- ✅ Multi-format export working
- ✅ File download serving ready

## Phase 7: Enhanced Metadata Review UI (5-10 hours)

### Tasks
1. **T087**: Implement inline editing in MetadataPanel
   - Make fields editable on click
   - Add edit/save/cancel buttons
   - Validate changes before save
   - Update Zustand store

2. **T088**: Add author/affiliation management
   - Add button to add new author
   - Add button to add new affiliation  
   - Edit existing entries
   - Delete entries with confirmation

3. **T089**: Add field validation
   - Show error messages per field
   - Highlight invalid fields
   - Block export if validation fails

4. **T090**: Add quick actions toolbar
   - Review button (full metadata view)
   - Save button (to store)
   - Discard button (reload from job)
   - Reset button (clear edits)

### Code Examples

**Enable inline editing in MetadataPanel.tsx**:
```typescript
const [editingField, setEditingField] = React.useState<string | null>(null)

const handleFieldClick = (field: string) => {
  setEditingField(field)
}

const handleSave = (field: keyof ExtractedMetadata, value: any) => {
  updateMetadataField(field, value)
  setEditingField(null)
}

// In render:
{editingField === 'title' ? (
  <input 
    value={metadata.title}
    onBlur={() => handleSave('title', (e.target as any).value)}
    autoFocus
  />
) : (
  <span onClick={() => handleFieldClick('title')}>{metadata.title}</span>
)}
```

**Add author management**:
```typescript
const handleAddAuthor = () => {
  const newAuthor: Author = {
    id: `author-${Date.now()}`,
    name: '',
    affiliation_ids: []
  }
  updateMetadataField('authors', [...metadata.authors, newAuthor])
}

const handleDeleteAuthor = (authorId: string) => {
  updateMetadataField(
    'authors',
    metadata.authors.filter(a => a.id !== authorId)
  )
}
```

## Phase 8: Testing & Quality (10-15 hours)

### Unit Tests
1. **T137**: Complete MetadataValidator tests
   - Test field length validation
   - Test pattern validation (DOI, ORCID, email)
   - Test confidence bounds

2. **T138**: Complete ExportControls tests
   - Test format selection
   - Test download functionality
   - Test error handling

### Integration Tests
1. **T140**: Complete API integration tests
   - Test /extract endpoint with mock PDF
   - Test polling mechanism
   - Test export generation
   - Test file download

### E2E Tests
1. **T142**: Implement Playwright E2E tests
   ```typescript
   test('complete upload-extract-export workflow', async ({ page }) => {
     // Upload PDF
     // Wait for extraction
     // Verify metadata displayed
     // Edit a field
     // Export to JSON
     // Download file
     // Verify file content
   })
   ```

### Coverage Target: 80%+
```bash
# Run with coverage
pytest --cov=src backend/tests
vitest --coverage frontend/tests
```

## Phase 9: Production Readiness (10-15 hours)

### Documentation
1. **T156**: API documentation
   - OpenAPI/Swagger spec
   - Endpoint descriptions
   - Error codes reference

2. **T157**: Developer setup guide
   - Environment variables
   - Database setup (when moving from in-memory)
   - Ollama setup
   - Running tests

3. **T158**: Deployment guide
   - Docker setup
   - Environment configuration
   - Database migrations
   - Backup/restore procedures

### Deployment
1. **T159**: Dockerize application
   ```dockerfile
   # Dockerfile.backend
   FROM python:3.10
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt
   COPY backend/src ./src
   CMD ["python", "-m", "uvicorn", "src.main:app"]

   # Dockerfile.frontend
   FROM node:18 AS build
   WORKDIR /app
   COPY frontend .
   RUN npm ci && npm run build
   
   FROM nginx:alpine
   COPY --from=build /app/dist /usr/share/nginx/html
   ```

2. **T160**: Set up CI/CD
   - GitHub Actions workflow
   - Run tests on push
   - Build Docker images
   - Deploy to staging

3. **T161**: Performance optimization
   - Enable gzip compression
   - Minimize frontend bundle
   - Cache static assets
   - Database indexing

### Security
1. **T162**: Security review
   - Input validation (all inputs validated)
   - CSRF protection
   - SQL injection prevention (N/A - no DB yet)
   - XSS prevention
   - Rate limiting

2. **T163**: Add authentication (optional for MVP)
   - JWT token support
   - User management
   - Role-based access

## Database Migration (When Ready)

When transitioning from in-memory to PostgreSQL:

```python
# backend/src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Models
class JobModel(Base):
    __tablename__ = "extraction_jobs"
    id: str = Column(String, primary_key=True)
    pdf_id: str = Column(String)
    status: str = Column(String)
    # ... other fields
    
# Replace job_manager.jobs dict with DB queries
```

## Testing Checklist

### Before Production
- [ ] 80%+ test coverage achieved
- [ ] All unit tests passing
- [ ] All integration tests passing  
- [ ] E2E tests passing on 3 browsers
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Documentation complete

### Load Testing
```python
# backend/tests/load_test.py
def test_concurrent_uploads():
    # Simulate 10 concurrent uploads
    # Verify system stability
    # Check response times
```

## Troubleshooting Guide

### If extraction hangs
- Check Ollama service is running: `curl http://localhost:11434/api/tags`
- Increase timeout in config: `EXTRACTION_TIMEOUT_SECONDS=120`
- Check system memory usage
- Review backend logs for errors

### If exports fail
- Verify metadata object has all required fields
- Check file system write permissions
- Verify MIME types are correct

### If tests fail
- Run with verbose output: `pytest -vv`
- Check Python version: `python --version` (requires 3.10+)
- Verify all dependencies installed: `pip install -r requirements.txt`

## Quick Commands

```bash
# Run backend
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend dev
cd frontend
npm run dev

# Run tests
pytest backend/tests
vitest run frontend/tests

# Run with coverage
pytest --cov=src backend/tests
vitest --coverage frontend/tests

# Build frontend
npm run build

# Lint code
npm run lint
black src
flake8 src

# Format code
npm run format
black src
isort src
```

## Expected Timeline

| Phase | Subtasks | Est. Time | Priority |
|-------|----------|-----------|----------|
| 7 | UI Polish | 4-6 hrs | HIGH |
| 8 | Testing | 10-15 hrs | HIGH |
| 9 | Production | 10-15 hrs | MEDIUM |
| DB | Database | 8-12 hrs | MEDIUM |
| CI/CD | Pipeline | 4-6 hrs | LOW |

**Total for MVP**: 36-54 hours (1 week with 2 developers)

## Getting Help

### Common Issues
- See STATUS_REPORT.md for feature summary
- Check docs/DEV_SETUP.md for environment setup
- Review specs/001-pdf-metadata-extraction/ for design docs

### Key Files to Review
- Backend: `backend/src/` (services, models, routes)
- Frontend: `frontend/src/` (components, hooks, services)
- Tests: `backend/tests/`, `frontend/tests/`
- Configuration: `.env`, `pyproject.toml`, `vite.config.ts`

## Next Developer Handoff

When handing off to next developer:
1. Share this guide
2. Ensure they follow DEV_SETUP.md
3. Have them run tests successfully
4. Review architecture in plan.md
5. Assign Phase 7 tasks to start
6. Set up daily standup (15 min)
7. Establish PR review process

Good luck! 🚀
