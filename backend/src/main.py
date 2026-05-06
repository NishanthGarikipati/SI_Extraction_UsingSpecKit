"""
FastAPI application entry point with middleware and routes configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import uuid
from datetime import datetime

from src.config import get_settings
from src.utils.logging import setup_logging, set_correlation_id, get_logger


# Setup logging
settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info("Application startup")
    yield
    # Shutdown
    logger.info("Application shutdown")


app = FastAPI(
    title="PDF Metadata Extraction API",
    description="API for extracting metadata from scientific PDFs using RAG with LLaMA 2",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom middleware for correlation IDs
@app.middleware("http")
async def add_correlation_id(request, call_next):
    """Add correlation ID to request context."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    set_correlation_id(correlation_id)
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.warning(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check API and service health."""
    return {
        "status": "healthy",
        "service": "pdf-metadata-extractor",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Import and include routes
from src.api.routes import router

app.include_router(router, tags=["extraction"])


# Health check at /api/health
@app.get("/api/health")
async def api_health_check():
    """Check API and service health (for /api prefix)."""
    return {
        "status": "healthy",
        "service": "pdf-metadata-extractor",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
