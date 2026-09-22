"""
ExpertLens AI — Application Configuration

Loads environment variables and provides typed settings for the entire application.
Supports Groq, HuggingFace, and Local LLM providers.
Database is SQLite for development, PostgreSQL-ready via connection string swap.
"""

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "ExpertLens AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server & CORS
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Database — SQLite for dev, swap to PostgreSQL via env
    DATABASE_URL: str = "sqlite+aiosqlite:///./expertlens.db"

    # ChromaDB & Vector Store
    CHROMA_PATH: str = str(ROOT_DIR / "data" / "chroma")
    CHROMA_COLLECTION: str = "transcript_chunks"

    # Embedding model (runs locally)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # LLM Provider: "groq", "huggingface", or "local"
    LLM_PROVIDER: str = "local"

    # Groq (https://console.groq.com)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # HuggingFace (https://huggingface.co/settings/tokens)
    HF_TOKEN: str = ""
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # Paths
    DATA_DIR: str = str(ROOT_DIR / "data")
    TRANSCRIPTS_DIR: str = str(ROOT_DIR / "data" / "transcripts")

    # Retrieval
    RETRIEVAL_TOP_K: int = 10
    RETRIEVAL_SCORE_THRESHOLD: float = 0.3

    # Quote validation
    QUOTE_SIMILARITY_THRESHOLD: float = 0.75

    # Evaluation Release Gates
    EVAL_MIN_ACCURACY: float = 0.85
    EVAL_MIN_GROUNDEDNESS: float = 0.90
    EVAL_MAX_HALLUCINATION: float = 0.05
    EVAL_MIN_CITATION_COVERAGE: float = 0.85

    model_config = SettingsConfigDict(
        env_file=[
            ".env",
            "../.env",
            str(ROOT_DIR / ".env"),
            str(ROOT_DIR / "backend" / ".env"),
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

