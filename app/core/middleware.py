"""
Custom middleware for FastAPI application.
Includes timeout middleware to prevent hanging requests.
"""
import asyncio
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status

from app.core.logging import get_logger

logger = get_logger(__name__)

# Default timeout: 30 seconds (matches frontend timeout)
DEFAULT_REQUEST_TIMEOUT = 30.0


class TimeoutMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request timeouts and prevent hanging requests.
    
    This middleware wraps all requests in a timeout to ensure they don't hang
    indefinitely. If a request takes longer than the timeout, it will be
    cancelled and return a 504 Gateway Timeout response.
    """
    
    def __init__(self, app, timeout: float = DEFAULT_REQUEST_TIMEOUT):
        super().__init__(app)
        self.timeout = timeout
    
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process request with timeout protection.
        
        Args:
            request: The incoming request
            call_next: The next middleware/route handler
            
        Returns:
            Response with timeout protection
        """
        # Skip timeout for streaming endpoints and long-running worksheet generation
        if request.url.path.endswith('/execute-stream') or '/stream' in request.url.path:
            return await call_next(request)
        if '/worksheets/generate' in request.url.path and request.method == 'POST':
            return await call_next(request)
        
        try:
            # Wrap the request handling in a timeout
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning(
                f"Request timeout after {self.timeout}s: {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "detail": f"Request timeout: The server took longer than {self.timeout} seconds to process the request. Please try again or contact support if the issue persists."
                }
            )
        except Exception as e:
            # Log unexpected errors but don't let them hang
            logger.error(f"Unexpected error in timeout middleware: {str(e)}", exc_info=True)
            raise
