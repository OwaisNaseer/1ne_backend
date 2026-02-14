"""
FastAPI application factory and main entry point.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.middleware import TimeoutMiddleware
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    AccountLockedError,
    InvalidTokenError,
    UserNotFoundError,
    UserAlreadyExistsError,
    EmailNotVerifiedError,
    PasswordValidationError,
    InvalidCredentialsError,
)
from app.api.v1 import router as v1_router

# Setup logging before creating the app
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="1ne.ai Backend API",
    description="AI-powered teacher assistant backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event():
    """Initialize backend on startup."""
    import os
    import platform
    from pathlib import Path
    
    # Auto-discover Poppler path if not set
    if not os.getenv("POPPLER_PATH") and platform.system() == "Windows":
        user_home = os.path.expanduser("~")
        poppler_paths = [
            r"C:\poppler\poppler-25.12.0\Library\bin",
            r"C:\poppler\Library\bin",
            os.path.join(user_home, r"Downloads\Release-25.12.0-0 (1)\poppler-25.12.0\Library\bin"),
            r"C:\Program Files\poppler\bin",
        ]
        
        for path_str in poppler_paths:
            poppler_dir = Path(path_str)
            if poppler_dir.is_dir():
                pdftoppm = poppler_dir / "pdftoppm.exe"
                if pdftoppm.exists():
                    os.environ["POPPLER_PATH"] = str(poppler_dir)
                    # Prepend to PATH for DLL resolution
                    current_path = os.environ.get("PATH", "")
                    if str(poppler_dir) not in current_path:
                        os.environ["PATH"] = f"{poppler_dir};{current_path}"
                    logger.info(f"Auto-discovered Poppler at startup: {poppler_dir}")
                    break
    
    # Auto-discover Tesseract if not set
    if not os.getenv("TESSERACT_CMD") and platform.system() == "Windows":
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path_str in tesseract_paths:
            if Path(path_str).exists():
                os.environ["TESSERACT_CMD"] = path_str
                logger.info(f"Auto-discovered Tesseract at startup: {path_str}")
                break
    
    logger.info("Backend startup initialization complete")

# Add CORS middleware FIRST (before timeout) to handle preflight requests
# CORS must be added before other middleware to properly handle OPTIONS requests
# IMPORTANT: When allow_credentials=True, you CANNOT use ["*"] - must list specific origins
# Since we use Authorization headers (not cookies), we can set allow_credentials=False
if settings.ENVIRONMENT == "dev":
    # In development, allow common localhost origins
    cors_origins = [
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # React default port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:5174",  # Vite alternative port
        "http://127.0.0.1:5174",
    ]
    # Also allow all origins for maximum compatibility in dev
    # But we'll use allow_credentials=False to make this work
    use_wildcard = True
else:
    # Get frontend URL from environment variable, fallback to localhost
    frontend_url = settings.FRONTEND_URL or "http://localhost:5173"
    
    cors_origins = [
        "https://1ne-frontend.vercel.app",  # Vercel production frontend
        frontend_url,  # Primary frontend URL from environment
        "http://localhost:5173",  # Vite default port (local dev)
        "http://localhost:3000",    # Alternative React port (local dev)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://localhost:5174",  # Vite alternative port
        "http://127.0.0.1:5174",
    ]
    
    # Add Vercel frontend URL if provided via environment variable
    vercel_url = settings.FRONTEND_URL
    if vercel_url and vercel_url not in cors_origins:
        cors_origins.append(vercel_url)
    
    # Also allow any Vercel preview deployments (pattern matching)
    # This allows preview deployments to work without manual configuration
    import os
    vercel_preview_url = os.getenv("VERCEL_URL")
    if vercel_preview_url:
        cors_origins.append(f"https://{vercel_preview_url}")
    
    # Remove duplicates while preserving order
    cors_origins = list(dict.fromkeys(cors_origins))
    use_wildcard = False

# Configure CORS middleware
# Note: allow_credentials=False because we use Authorization headers, not cookies
# This allows us to use wildcard origins in dev mode if needed
if use_wildcard and settings.ENVIRONMENT == "dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in dev
        allow_credentials=False,  # Must be False when using wildcard
        allow_methods=["*"],  # Allow all HTTP methods (including OPTIONS)
        allow_headers=["*"],  # Allow all headers (including Authorization)
        expose_headers=["X-Worksheet-Cache", "X-Request-Id"],  # Expose custom headers to frontend
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,  # We use Authorization headers, not cookies
        allow_methods=["*"],  # Allow all HTTP methods (including OPTIONS)
        allow_headers=["*"],  # Allow all headers (including Authorization)
        expose_headers=["X-Worksheet-Cache", "X-Request-Id"],  # Expose custom headers to frontend
    )

# Add timeout middleware AFTER CORS (so CORS handles preflight first)
app.add_middleware(
    TimeoutMiddleware,
    timeout=30.0,  # 30 seconds timeout to match frontend
)


# ========== Global Exception Handlers ==========

@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


@app.exception_handler(AuthorizationError)
async def authorization_error_handler(request: Request, exc: AuthorizationError):
    """Handle authorization errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_error_handler(request: Request, exc: InvalidCredentialsError):
    """Handle invalid credentials errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_error_handler(request: Request, exc: UserNotFoundError):
    """Handle user not found errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_error_handler(request: Request, exc: UserAlreadyExistsError):
    """Handle user already exists errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(EmailNotVerifiedError)
async def email_not_verified_error_handler(request: Request, exc: EmailNotVerifiedError):
    """Handle email not verified errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(PasswordValidationError)
async def password_validation_error_handler(request: Request, exc: PasswordValidationError):
    """Handle password validation errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(InvalidTokenError)
async def invalid_token_error_handler(request: Request, exc: InvalidTokenError):
    """Handle invalid token errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


@app.exception_handler(AccountLockedError)
async def account_locked_error_handler(request: Request, exc: AccountLockedError):
    """Handle account locked errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {str(exc)}", exc_info=True)
    
    # Check for common integrity errors
    error_str = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    
    if "unique constraint" in error_str.lower() or "duplicate key" in error_str.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": "A record with this information already exists"},
        )
    elif "foreign key constraint" in error_str.lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid reference to related record"},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Database constraint violation"},
        )


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    """Handle database operational errors."""
    logger.error(f"Database operational error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": "Database service temporarily unavailable. Please try again later."},
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle general SQLAlchemy errors."""
    logger.error(f"Database error: {str(exc)}", exc_info=True)
    
    # In development, provide more details for debugging
    if settings.ENVIRONMENT != "prod":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database error occurred. Please try again later.",
                "error": str(exc),
                "type": type(exc).__name__,
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occurred. Please try again later."},
        )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning(f"Value error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Check if it's already an HTTPException (should have been handled by specific handlers)
    from fastapi import HTTPException as FastAPIHTTPException
    if isinstance(exc, FastAPIHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    # In production, don't expose internal error details
    if settings.ENVIRONMENT == "prod":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred. Please try again later."},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An internal server error occurred.",
                "error": str(exc),
                "type": type(exc).__name__,
            },
        )


@app.get("/health")
async def health_check():
    """Health check endpoint with database connectivity check."""
    from app.db.session import SessionLocal
    from sqlalchemy import text
    
    try:
        # Check database connection
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            db_status = "connected"
        finally:
            db.close()
        return {"status": "ok", "database": db_status}
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        # Return 200 OK even if database is disconnected - backend is still running
        # This prevents frontend from thinking backend is down
        return {
            "status": "degraded", 
            "database": "disconnected", 
            "message": "Backend is running but database is unavailable",
            "error": str(e) if settings.ENVIRONMENT != "prod" else None
        }


@app.get("/api/routes")
async def list_routes():
    """List all registered routes for debugging."""
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes_info.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', None)
            })
    return {
        "total_routes": len(routes_info),
        "routes": sorted(routes_info, key=lambda x: x["path"])
    }


@app.get("/api/v1/test")
async def test_endpoint():
    """Simple test endpoint that doesn't require database - for connection testing."""
    import datetime
    return {
        "status": "ok",
        "message": "Backend API is accessible",
        "cors": "enabled",
        "timestamp": datetime.datetime.now().isoformat()
    }


# Register API v1 routers (they already include /api/v1 prefixes)
try:
    app.include_router(v1_router)
    logger.info("API v1 router registered successfully")
    # Log registered routes for debugging
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            logger.debug(f"Registered route: {list(route.methods)} {route.path}")
except Exception as e:
    logger.error(f"Failed to register API v1 router: {e}", exc_info=True)
    raise

# Mount static files for profile pictures
from app.core.config import settings
profile_pictures_dir = Path(settings.PROFILE_PICTURES_DIR)
profile_pictures_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/profile_pictures", StaticFiles(directory=str(profile_pictures_dir)), name="profile_pictures")
