"""
Database session management.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import Base

logger = get_logger(__name__)

# Create SQLAlchemy engine with connection timeout to prevent hanging
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.ENVIRONMENT == "dev",  # Echo SQL queries in dev mode
    connect_args={
        "connect_timeout": 2,  # 2 second connection timeout - very fast
    } if "postgresql" in settings.DATABASE_URL else {},
    pool_timeout=2,  # 2 second pool timeout - very fast
    pool_reset_on_return='commit',  # Reset connection on return
    pool_recycle=300,  # Recycle connections after 5 minutes
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = None
    try:
        db = SessionLocal()
        yield db
        db.commit()
    except Exception as e:
        if db:
            db.rollback()
        # Don't raise - let endpoint handle it
        logger.error(f"Database session error: {e}")
        raise
    finally:
        if db:
            db.close()

