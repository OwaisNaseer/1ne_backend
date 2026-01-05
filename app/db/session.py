"""
Database session management with SSL support for cloud databases.
Includes retry logic and robust error handling for connection issues.
"""
from typing import Generator
import time

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, DisconnectionError, TimeoutError

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import Base

logger = get_logger(__name__)

# Determine if connecting to Supabase or other cloud database (requires SSL)
is_cloud_db = "supabase.co" in settings.DATABASE_URL or "pooler.supabase.com" in settings.DATABASE_URL

# Create SQLAlchemy engine optimized for cloud databases with SSL
# Add statement timeout to prevent hanging queries (10 seconds)
statement_timeout = "-c statement_timeout=10000"  # 10 seconds in milliseconds
timezone_setting = "-c timezone=utc"
db_options = f"{statement_timeout} {timezone_setting}"

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using (important for cloud DBs)
    echo=settings.ENVIRONMENT == "dev",  # Echo SQL queries in dev mode
    connect_args={
        "connect_timeout": 10,  # Connection timeout (increased for better reliability)
        "sslmode": "require" if is_cloud_db else "prefer",  # SSL required for Supabase/cloud databases
        "options": db_options,  # Statement timeout + timezone
    } if "postgresql" in settings.DATABASE_URL else {},
    pool_timeout=30,  # Pool timeout (30 seconds - increased for better reliability)
    pool_size=10,  # Increased pool size for better concurrency
    max_overflow=20,  # Allow more overflow connections
    pool_reset_on_return='commit',  # Reset connection on return
    pool_recycle=3600,  # Recycle connections after 1 hour
    poolclass=None,  # Use default queue pool
)

# Add connection pool event listeners for better error handling
@event.listens_for(engine, "connect")
def set_connection_pragmas(dbapi_conn, connection_record):
    """Set connection-level settings."""
    try:
        # Set timezone to UTC using cursor (psycopg2 requires cursor, not direct execute)
        cursor = dbapi_conn.cursor()
        cursor.execute("SET timezone TO 'UTC'")
        cursor.close()
    except Exception as e:
        logger.warning(f"Failed to set connection pragmas: {e}")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Handle connection checkout with retry logic."""
    # Connection is already checked by pool_pre_ping, but we can add additional logic here
    pass

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    Includes retry logic for connection failures.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = None
    max_retries = 3
    retry_delay = 0.5  # Start with 0.5 seconds
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Skip connection test to speed up - pool_pre_ping already handles this
            # db.execute(text("SELECT 1"))  # Removed to speed up connection
            yield db
            db.commit()
            break  # Success, exit retry loop
        except (OperationalError, DisconnectionError, TimeoutError) as e:
            if db:
                try:
                    db.rollback()
                    db.close()
                except Exception:
                    pass
                db = None
            
            error_msg = str(e).lower()
            is_connection_error = any(keyword in error_msg for keyword in [
                "connection", "timeout", "network", "could not connect",
                "server closed", "connection lost", "connection refused",
                "temporarily unavailable", "pool"
            ])
            
            if attempt < max_retries - 1 and is_connection_error:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"Database connection failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                    f"Retrying in {wait_time:.2f} seconds..."
                )
                time.sleep(wait_time)
                continue
            else:
                logger.error(f"Database connection error after {attempt + 1} attempts: {e}", exc_info=True)
                raise
        except Exception as e:
            if db:
                try:
                    db.rollback()
                except Exception:
                    pass
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            if db and attempt == max_retries - 1:  # Only close on final attempt
                try:
                    db.close()
                except Exception:
                    pass

