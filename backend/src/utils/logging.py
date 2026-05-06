"""
Logging configuration with structured logging and correlation IDs
"""
import logging
import logging.config
import json
import uuid
from datetime import datetime
from typing import Optional
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger


# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


def get_correlation_id() -> str:
    """Get or create correlation ID for request tracking."""
    correlation_id = correlation_id_var.get()
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
        correlation_id_var.set(correlation_id)
    return correlation_id


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(correlation_id)


class CorrelationIdFilter(logging.Filter):
    """Logging filter that adds correlation ID to all log records."""
    
    def filter(self, record):
        record.correlation_id = get_correlation_id()
        record.timestamp = datetime.utcnow().isoformat()
        return True


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure application logging with JSON formatting for production.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(timestamp)s %(level)s %(name)s %(message)s %(correlation_id)s",
            },
        },
        "filters": {
            "correlation": {
                "()": CorrelationIdFilter,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "filters": ["correlation"],
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": level,
                "handlers": ["console"],
            },
            "uvicorn": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with correlation ID filter.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add correlation ID filter to all handlers
    for handler in logger.handlers:
        if not any(isinstance(f, CorrelationIdFilter) for f in handler.filters):
            handler.addFilter(CorrelationIdFilter())
    
    return logger


def log_extraction_start(job_id: str, filename: str, file_size: int) -> None:
    """Log extraction job start."""
    logger = get_logger(__name__)
    logger.info(
        f"Extraction started",
        extra={
            "job_id": job_id,
            "filename": filename,
            "file_size_mb": file_size / (1024 * 1024),
        }
    )


def log_extraction_complete(job_id: str, elapsed_ms: int, success: bool, error: Optional[str] = None) -> None:
    """Log extraction job completion."""
    logger = get_logger(__name__)
    if success:
        logger.info(
            f"Extraction completed",
            extra={
                "job_id": job_id,
                "elapsed_ms": elapsed_ms,
                "status": "success",
            }
        )
    else:
        logger.error(
            f"Extraction failed",
            extra={
                "job_id": job_id,
                "elapsed_ms": elapsed_ms,
                "status": "failed",
                "error": error,
            }
        )
