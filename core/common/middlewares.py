from functools import wraps
from flask import request, g, current_app
import time
import logging
from typing import Callable, Any

from core.common.exceptions import JeruyiqException

logger = logging.getLogger(__name__)

def error_handler(error: Exception) -> tuple[dict, int]:
    """Handle different types of exceptions and return appropriate responses."""
    if isinstance(error, JeruyiqException):
        response = {
            'error': error.__class__.__name__,
            'message': error.message
        }
        if hasattr(error, 'errors'):
            response['errors'] = error.errors
        return response, error.status_code
    
    # Log unexpected errors
    logger.exception("Unexpected error occurred")
    return {
        'error': 'InternalServerError',
        'message': 'An unexpected error occurred'
    }, 500

def request_logger(f: Callable) -> Callable:
    """Log request details."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        # Start timer
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url}\n"
            f"Headers: {dict(request.headers)}\n"
            f"Body: {request.get_json(silent=True)}"
        )
        
        # Execute view function
        response = f(*args, **kwargs)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Response: {response}\n"
            f"Duration: {duration:.2f}s"
        )
        
        return response
    return decorated_function

def setup_request_context() -> None:
    """Setup context for each request."""
    g.request_id = request.headers.get('X-Request-ID', '')
    g.start_time = time.time()

def add_cors_headers(response: Any) -> Any:
    """Add CORS headers to response."""
    response.headers['Access-Control-Allow-Origin'] = current_app.config.get('CORS_ORIGIN', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response
