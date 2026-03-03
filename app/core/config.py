"""
Application configuration using Pydantic BaseSettings.
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/1ne_db"

    # Environment
    ENVIRONMENT: str = "dev"  # dev, staging, prod

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # Access tokens expire after 1 day (24 hours)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1       # Refresh tokens expire after 1 day

    # Password Policy
    PASSWORD_MIN_LENGTH: int = 10
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # Account Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_LOGIN_PER_IP: int = 5

    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@1ne.ai"
    SMTP_FROM_NAME: str = "1ne.ai"
    FRONTEND_URL: str = "http://localhost:5173"

    # Refresh Token Rotation
    REFRESH_TOKEN_ROTATION_ENABLED: bool = True

    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    PROFILE_PICTURES_DIR: str = "uploads/profile_pictures"
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_IMAGE_EXTENSIONS: list[str] = [".jpg", ".jpeg", ".png", ".webp"]

    # Super Admin Setup (for first-time initialization)
    SUPER_ADMIN_EMAIL: Optional[str] = None
    SUPER_ADMIN_PASSWORD: Optional[str] = None
    SUPER_ADMIN_FIRST_NAME: str = "Super"
    SUPER_ADMIN_LAST_NAME: str = "Admin"

    # Content Ingestion Configuration
    OCR_ENGINE: str = "tesseract"  # tesseract | easyocr | mathpix
    OCR_PROVIDER: str = "tesseract"  # tesseract | azure | google | mathpix
    # Professional OCR: policy-driven control (international, multi-board)
    OCR_MODE: str = "local"  # local = never call external APIs; api = allow API engines if keys present
    OCR_ENGINE_DEFAULT: str = "tesseract"  # default when pack has ocr_policy=auto
    OCR_FALLBACK_ENGINE: str = "tesseract"  # fallback when API keys missing
    TEXT_EXTRACTOR_PROVIDER: str = "pdfplumber"  # pdfplumber | pymupdf | ...
    EMBEDDING_PROVIDER: str = "fake"  # fake | local | openai (free mode: fake or local)
    VECTOR_STORE: str = "pgvector"  # pgvector | qdrant | pinecone
    MATH_PROVIDER: str = "baseline"  # baseline | mathpix (mathpix later)
    # Chunking profiles
    # Digital documents (PDF with reliable text layer)
    CHUNK_SIZE_TOKENS_DIGITAL: int = 500
    CHUNK_OVERLAP_TOKENS_DIGITAL: int = 50
    # OCR / scanned documents (smaller chunks to increase coverage; target 200–250)
    CHUNK_SIZE_TOKENS_OCR: int = 220
    CHUNK_OVERLAP_TOKENS_OCR: int = 50
    # Global defaults (backwards-compat; used if profile-specific vars are not referenced)
    CHUNK_SIZE_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50
    MIN_CHARS_PER_PAGE: int = 100
    MIN_CHARS_EXTRACT: int = 1  # Min total chars after extract/OCR to pass checkpoint
    SCANNED_THRESHOLD_CHARS: int = 50  # Below this = scanned, needs OCR
    # Adaptive chunking: minimum chunks for OCR documents before rechunking
    OCR_MIN_CHUNKS_THRESHOLD: int = 20
    # For small OCR docs (pages < OCR_MIN_PAGES_FOR_THRESHOLD): use lower threshold
    OCR_MIN_PAGES_FOR_THRESHOLD: int = 30
    OCR_MIN_CHUNKS_THRESHOLD_SMALL: int = 10
    # Rechunk size when below threshold (deterministic; no guesswork)
    OCR_RECHUNK_SIZE_TOKENS: int = 200
    MAX_FILE_SIZE_MB: int = 50  # Max document file size
    DOCUMENTS_DIR: str = "uploads/documents"  # Document storage directory
    # Free-mode embedding
    FAKE_EMBEDDING_DIM: int = 384
    LOCAL_EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Worksheet generation: hard cap so requests never hang (seconds); configurable via env
    WORKSHEET_GENERATION_TIMEOUT_SECONDS: float = 180.0
    # When False: skip cache lookup and cache write (no worksheet_cache DB dependency)
    WORKSHEET_CACHE_ENABLED: bool = False
    # Max repair attempts for difficulty validation before downgrade or best-effort return
    WORKSHEET_MAX_REPAIR_ATTEMPTS: int = 3
    # When True, auto-downgrade difficulty (hard→medium→easy) if validation fails after repairs
    WORKSHEET_ENABLE_DIFFICULTY_DOWNGRADE: bool = True
    # Jaccard/similarity threshold above which a question is considered duplicate of a previous one (0–1)
    WORKSHEET_DEDUPE_THRESHOLD: float = 0.85
    # Token overlap threshold above which a question is considered copying pack text (0–1); rewrite if exceeded
    WORKSHEET_COPY_OVERLAP_THRESHOLD: float = 0.35
    # Role-bucket retrieval: minimum chunks per bucket before backfill; backfill from remaining relevant chunks
    BUCKET_MIN_TARGET: int = 4
    # Role tagging: min chars for exercise/exam blocks (anti false-positive)
    ROLE_MIN_CHARS_FOR_QUESTION_BLOCK: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()

