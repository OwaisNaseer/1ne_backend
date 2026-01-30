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
    TEXT_EXTRACTOR_PROVIDER: str = "pdfplumber"  # pdfplumber | pymupdf | ...
    EMBEDDING_PROVIDER: str = "fake"  # fake | local | openai (free mode: fake or local)
    VECTOR_STORE: str = "pgvector"  # pgvector | qdrant | pinecone
    MATH_PROVIDER: str = "baseline"  # baseline | mathpix (mathpix later)
    CHUNK_SIZE_TOKENS: int = 500
    CHUNK_OVERLAP_TOKENS: int = 50
    MIN_CHARS_PER_PAGE: int = 100
    MIN_CHARS_EXTRACT: int = 1  # Min total chars after extract/OCR to pass checkpoint
    SCANNED_THRESHOLD_CHARS: int = 50  # Below this = scanned, needs OCR
    MAX_FILE_SIZE_MB: int = 50  # Max document file size
    DOCUMENTS_DIR: str = "uploads/documents"  # Document storage directory
    # Free-mode embedding
    FAKE_EMBEDDING_DIM: int = 384
    LOCAL_EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

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

