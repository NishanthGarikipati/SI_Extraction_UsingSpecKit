import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Ollama Configuration
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    extraction_timeout_seconds: int = 30
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    allow_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins(self) -> list[str]:
        """Parse ALLOW_ORIGINS string into list."""
        return [origin.strip() for origin in self.allow_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
