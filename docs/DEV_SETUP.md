# Development Environment Setup

## Prerequisites

- **Python**: 3.10+ (check with `python --version`)
- **Node.js**: 18+ and npm (check with `node --version` and `npm --version`)
- **Git**: For version control
- **Ollama**: For running LLaMA 2 locally (see below)

## Backend Setup

### 1. Initialize Python Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create or edit `.env` file in `backend/` directory:

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
EXTRACTION_TIMEOUT_SECONDS=30
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
ALLOW_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
```

### 4. Start Backend Development Server

```bash
# From backend directory with venv activated
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## Ollama Setup

### 1. Install Ollama

**macOS**:
```bash
brew install ollama
```

**Linux**:
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows**:
Download from https://ollama.ai

### 2. Pull LLaMA 2 Model

```bash
ollama pull llama2
```

### 3. Run Ollama Service

```bash
ollama serve
```

Ollama will be available at: `http://localhost:11434`

## Development Workflow

### Terminal 1: Ollama Service
```bash
ollama serve
```

### Terminal 2: Backend API
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Frontend Dev Server
```bash
cd frontend
npm run dev
```

## Testing

### Backend Unit Tests

```bash
cd backend
source venv/bin/activate
pytest tests/unit/ -v
```

### Backend Integration Tests

```bash
cd backend
source venv/bin/activate
pytest tests/integration/ -v
```

### Frontend Unit Tests

```bash
cd frontend
npm run test
```

### Frontend E2E Tests

```bash
cd frontend
npm run e2e
```

## Code Quality

### Backend Linting

```bash
cd backend
flake8 src/
black src/ --check
mypy src/
```

### Frontend Linting

```bash
cd frontend
npm run lint
```

### Format Code

```bash
# Backend
cd backend
black src/

# Frontend
cd frontend
npm run format
```

## Build for Production

### Backend

```bash
cd backend
# Backend runs from source with uvicorn
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

## Troubleshooting

### Python Virtual Environment Issues

```bash
# Recreate venv if corrupted
rm -rf backend/venv
python -m venv backend/venv
```

### Ollama Not Connecting

1. Ensure Ollama is running: `ollama serve`
2. Check OLLAMA_HOST in `.env` matches Ollama's bind address
3. Verify model exists: `ollama list`

### Port Already in Use

```bash
# Find process using port 8000 (backend)
lsof -i :8000
# or Windows:
netstat -ano | findstr :8000

# Kill process and restart
```

### Dependencies Issues

```bash
# Backend: Reinstall dependencies
cd backend
pip install --force-reinstall -r requirements.txt

# Frontend: Clear npm cache and reinstall
cd frontend
npm cache clean --force
rm -rf node_modules
npm install
```

## IDE Configuration

### VS Code Extensions

- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint
- Tailwind CSS IntelliSense

### Launch Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["src.main:app", "--reload"],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```
