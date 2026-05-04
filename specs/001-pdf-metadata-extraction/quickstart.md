# Quick-Start Guide: PDF Metadata Extraction

**Phase**: 1 (Design & Contracts)  
**Date**: 2026-05-04  
**Status**: Complete

---

## Overview

This guide provides step-by-step instructions for setting up and running the PDF Metadata Extraction application for the first time. The application consists of a React frontend and Python backend with local Ollama LLaMA 2 inference.

**Estimated Setup Time**: 30-45 minutes (depending on Ollama model download)

---

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (WSL2 recommended for Windows)
- **RAM**: 8GB minimum (16GB recommended for LLaMA 2)
- **Disk Space**: 10GB free (for Ollama model download)
- **GPU**: Optional but recommended (NVIDIA CUDA, Apple Silicon, AMD ROCm)

### Software Requirements
- **Node.js**: v18.0.0 or higher (for frontend)
- **Python**: 3.10 or higher (for backend)
- **Docker** (optional, for containerized Ollama)
- **Git**: For version control

### Browser Support
- Chrome/Chromium: Latest version
- Firefox: Latest version
- Safari: 15+
- Edge: Latest version

---

## Part 1: Install Ollama & LLaMA 2

Ollama provides the local LLM inference engine for metadata extraction.

### Step 1.1: Download and Install Ollama

**macOS**:
```bash
# Download from https://ollama.ai or use Homebrew
brew install ollama

# Start Ollama service
ollama serve
```

**Linux** (Ubuntu/Debian):
```bash
curl https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

**Windows** (WSL2):
```bash
# In WSL2 terminal
curl https://ollama.ai/install.sh | sh
ollama serve
```

**Verification**:
```bash
# In a new terminal, test Ollama is running
curl http://localhost:11434/api/tags

# Expected output:
# {"models":[]}  # Empty initially, will populate after pulling model
```

### Step 1.2: Pull LLaMA 2 Model

```bash
# Pull the 7B parameter model (recommended for balance of speed/accuracy)
ollama pull llama2:7b-q4

# Alternative: Larger model for higher accuracy (slower)
# ollama pull llama2:13b-q4

# Alternative: Smaller model for faster inference (lower accuracy)
# ollama pull llama2:7b

# Verify model is installed
ollama list
```

**Expected Output**:
```
NAME                SIZE    DIGEST
llama2:7b-q4        4.0GB   abc123...
```

**Time to Download**: ~10-15 minutes (7B-q4 model is ~4GB)

### Step 1.3: Test Ollama Inference (Optional)

```bash
# Test the model with a simple prompt
curl http://localhost:11434/api/generate -d '{
  "model": "llama2:7b-q4",
  "prompt": "Explain metadata extraction",
  "stream": false
}'
```

---

## Part 2: Set Up Python Backend

### Step 2.1: Clone/Create Backend Directory

```bash
# Navigate to project root
cd SI_Extraction_UsingSpecKit

# Create backend directory
mkdir -p backend
cd backend
```

### Step 2.2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (WSL2):
source venv/bin/activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### Step 2.3: Install Backend Dependencies

```bash
# Create requirements.txt (see implementation phase for full list)
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.4.2
pydantic-settings==2.0.3
pdfplumber==0.10.3
pypdf==3.17.1
python-multipart==0.0.6
aiofiles==23.2.1
requests==2.31.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.0
langchain==0.1.0
ollama==0.0.39
EOF

# Install dependencies
pip install -r requirements.txt
```

### Step 2.4: Set Up Backend Configuration

```bash
# Create .env file for backend configuration
cat > .env << 'EOF'
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2:7b-q4
EXTRACTION_TIMEOUT_SECONDS=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS Configuration
FRONTEND_URL=http://localhost:5173
ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
EOF
```

### Step 2.5: Create Backend Structure

```bash
# Create source directory structure
mkdir -p src/{models,services,api,utils,prompts}
touch src/__init__.py
touch src/{models,services,api,utils,prompts}/__init__.py

# Create main.py entry point (see implementation phase)
cat > src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PDF Metadata Extraction API", version="1.0.0")

# CORS middleware
origins = os.getenv("ALLOW_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
EOF
```

### Step 2.6: Start Backend Service

```bash
# Make sure venv is activated
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Start FastAPI backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Verify Backend**:
```bash
# In a new terminal
curl http://localhost:8000/api/health

# Expected output:
# {"status":"healthy","version":"1.0.0"}
```

---

## Part 3: Set Up React Frontend

### Step 3.1: Create Frontend Directory

```bash
# Navigate to project root
cd SI_Extraction_UsingSpecKit

# Create frontend with Vite
npm create vite@latest frontend -- --template react-ts

# Or manually create directory
mkdir -p frontend
cd frontend
```

### Step 3.2: Install Frontend Dependencies

```bash
# Initialize if not created by Vite
npm init -y

# Install core dependencies
npm install react@18.2.0 react-dom@18.2.0 typescript@5.0.0

# Install UI and utility libraries
npm install react-pdf pdfjs-dist tailwindcss postcss autoprefixer zustand react-hook-form axios

# Install dev dependencies
npm install -D vite @vitejs/plugin-react @types/react @types/react-dom vitest @testing-library/react

# Initialize Tailwind CSS
npx tailwindcss init -p
```

### Step 3.3: Configure Vite

```bash
# Create vite.config.ts
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
EOF
```

### Step 3.4: Create Directory Structure

```bash
# Create source directory structure
mkdir -p src/{components,pages,services,types,hooks,styles}
touch src/{components,pages,services,types,hooks,styles}/.keep

# Create entry points
cat > src/main.tsx << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './pages/App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF

cat > index.html << 'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>PDF Metadata Extraction</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF
```

### Step 3.5: Configure Tailwind CSS

```bash
# Create tailwind.config.ts
cat > tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config
EOF

# Create postcss.config.cjs
cat > postcss.config.cjs << 'EOF'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF
```

### Step 3.6: Start Frontend Development Server

```bash
# Make sure you're in frontend directory
cd SI_Extraction_UsingSpecKit/frontend

# Install dependencies (if not done)
npm install

# Start dev server
npm run dev

# Expected output:
# VITE v4.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

**Verify Frontend**:
Open browser and navigate to `http://localhost:5173/` - should see React starter page

---

## Part 4: Verify Full Integration

### Check All Services Running

```bash
# 1. Check Ollama
curl http://localhost:11434/api/tags
# Expected: {"models":[{"name":"llama2:7b-q4",...}]}

# 2. Check Backend
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","version":"1.0.0"}

# 3. Check Frontend
# Open browser: http://localhost:5173/
# Should load without errors
```

### Run First Test Extraction

```bash
# Create sample PDF for testing (or use existing)
# Upload via web UI at http://localhost:5173/

# Monitor backend logs for processing:
# - PDF upload received
# - Text extraction started
# - LLM extraction started
# - Metadata parsed
# - Response sent

# Check frontend displays:
# - PDF rendered on right panel
# - Metadata list appears on left panel after 10-30 seconds
```

---

## Part 5: Development Workflow

### Terminal 1: Ollama (Keep running)
```bash
ollama serve
```

### Terminal 2: Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

### Terminal 4: Testing/Utilities
```bash
# Available for running tests, linting, etc.
cd backend && pytest
# or
cd frontend && npm test
```

---

## Troubleshooting

### Ollama Not Responding
```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
ollama serve

# Verify port 11434 is accessible
netstat -an | grep 11434
```

### Backend Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Verify virtual environment activated
which python  # Should show venv path

# Check for port conflicts
lsof -i :8000  # Kill process if needed
```

### Frontend Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf dist .vite
npm run dev
```

### PDF Won't Upload
```bash
# Check browser console (F12) for errors
# Check backend logs for error details
# Verify PDF file is valid (< 50MB)
# Check CORS settings in backend
```

### Extraction Timeout
```bash
# If taking > 30 seconds, may need:
# 1. GPU acceleration (check CUDA installation)
# 2. Larger model (try llama2:7b instead of q4)
# 3. More RAM available
# 4. Check Ollama logs for errors
```

---

## Next Steps

1. **Explore the UI** - Upload a sample academic PDF and test the full workflow
2. **Review Logs** - Check browser console and backend logs for insights
3. **Validate Output** - Compare extracted metadata with PDF source
4. **Test Export** - Generate JSON/XML/TOON files and verify format
5. **Read Implementation Docs** - See `tasks.md` for detailed development guidance

---

## Useful Commands

```bash
# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pytest tests/                           # Run tests
python -m flake8 src/                  # Lint code
python -m black src/                   # Format code
python -m uvicorn src.main:app --reload

# Frontend
cd frontend
npm install
npm run dev                             # Start dev server
npm run build                           # Production build
npm test                                # Run tests
npm run lint                            # Lint code
npm run format                          # Format code

# Docker (if using containers)
docker-compose up                       # Start all services
docker-compose down                     # Stop services
```

---

## Performance Tips

1. **Use GPU**: Install CUDA drivers for NVIDIA, ROCm for AMD, or Metal for Apple Silicon
2. **Use Quantized Model**: `llama2:7b-q4` is faster than `llama2:7b`
3. **Enable Caching**: Backend caches extraction results for duplicate PDFs
4. **Lazy Load UI**: Frontend lazy-loads PDF viewer and export utilities
5. **Monitor Memory**: Keep an eye on Ollama and Node.js memory usage

---

## Production Deployment

For production, see deployment guide: `docs/DEPLOYMENT.md`

Key considerations:
- Use production Ollama service (GPU server or cloud)
- Set environment variables via secrets manager
- Enable HTTPS/TLS
- Implement rate limiting
- Add authentication/authorization
- Deploy frontend to CDN
- Use managed databases if needed
- Set up monitoring and alerting

---

## Support & Documentation

- API Specification: [contracts/api-specification.md](contracts/api-specification.md)
- Export Formats: [contracts/export-formats.md](contracts/export-formats.md)
- Data Model: [data-model.md](data-model.md)
- Architecture: `docs/ARCHITECTURE.md` (coming in implementation)
- FAQ: `docs/FAQ.md` (coming in implementation)
