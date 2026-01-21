"""Custom exception classes and error handling for Retail Analytics Dashboard.

This module provides centralized error handling with custom exception classes,
Flask error handlers, and logging integration.
"""

import logging
import traceback
from typing import Dict, Any, Optional, Tuple
from functools import wraps
from flask import jsonify, request
from werkzeug.exceptions import HTTPException
import sys


logger = logging.getLogger(__name__)


# ==================== Custom Exception Classes ====================

class RetailAnalyticsError(Exception):
    """Base exception class for all custom errors."""
    
    def __init__(self, message: str, status_code: int = 500, payload: Optional[Dict] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        rv = dict(self.payload or {})
        rv["error"] = self.__class__.__name__
        rv["message"] = self.message
        rv["status_code"] = self.status_code
        return rv


class DatabaseError(RetailAnalyticsError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


class ValidationError(RetailAnalyticsError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Invalid input data", **kwargs):
        super().__init__(message, status_code=400, **kwargs)


class AuthenticationError(RetailAnalyticsError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class AuthorizationError(RetailAnalyticsError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class ResourceNotFoundError(RetailAnalyticsError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


class DataProcessingError(RetailAnalyticsError):
    """Raised when data processing fails."""
    
    def __init__(self, message: str = "Data processing failed", **kwargs):
        super().__init__(message, status_code=422, **kwargs)


class RateLimitError(RetailAnalyticsError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", **kwargs):
        super().__init__(message, status_code=429, **kwargs)


class ConfigurationError(RetailAnalyticsError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str = "Invalid configuration", **kwargs):
        super().__init__(message, status_code=500, **kwargs)


# ==================== Error Handlers ====================

def register_error_handlers(app):
    """Register error handlers with Flask application.
    
    Args:
        app: Flask application instance.
    """
    
    @app.errorhandler(RetailAnalyticsError)
    def handle_custom_error(error: RetailAnalyticsError):
        """Handle custom application errors."""
        logger.error(
            f"{error.__class__.__name__}: {error.message}",
            extra={
                "status_code": error.status_code,
                "payload": error.payload,
                "path": request.path,
                "method": request.method,
            }
        )
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(
            f"HTTP {error.code}: {error.description}",
            extra={
                "path": request.path,
                "method": request.method,
            }
        )
        return jsonify({
            "error": error.name,
            "message": error.description,
            "status_code": error.code,
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Handle unexpected errors."""
        logger.critical(
            f"Unexpected error: {str(error)}",
            exc_info=True,
            extra={
                "path": request.path,
                "method": request.method,
                "traceback": traceback.format_exc(),
            }
        )
        
        # Don't expose internal error details in production
        if app.debug:
            return jsonify({
                "error": "InternalServerError",
                "message": str(error),
                "traceback": traceback.format_exc(),
                "status_code": 500,
            }), 500
        else:
            return jsonify({
                "error": "InternalServerError",
                "message": "An unexpected error occurred. Please contact support.",
                "status_code": 500,
            }), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors."""
        logger.info(f"404 Not Found: {request.path}")
        return jsonify({
            "error": "NotFound",
            "message": f"The requested URL {request.path} was not found.",
            "status_code": 404,
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        logger.info(f"405 Method Not Allowed: {request.method} {request.path}")
        return jsonify({
            "error": "MethodNotAllowed",
            "message": f"The method {request.method} is not allowed for {request.path}.",
            "status_code": 405,
        }), 405


# ==================== Decorator for Error Handling ====================

def handle_errors(func):
    """Decorator to handle errors in route functions.
    
    This decorator catches exceptions, logs them, and returns appropriate
    JSON error responses.
    
    Usage:
        @app.route('/api/data')
        @handle_errors
        def get_data():
            # Your code here
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RetailAnalyticsError:
            # Re-raise custom errors to be handled by error handlers
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(
                f"Error in {func.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                }
            )
            # Re-raise to be handled by error handlers
            raise
    return wrapper


# ==================== Logging Configuration ====================

def setup_logging(app):
    """Configure application logging.
    
    Args:
        app: Flask application instance.
    """
    log_level = getattr(logging, app.config["LOG_LEVEL"].upper())
    log_format = app.config["LOG_FORMAT"]
    log_file = app.config["LOG_FILE"]
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file),
        ]
    )
    
    # Configure Flask app logger
    app.logger.setLevel(log_level)
    
    # Reduce noise from third-party libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger.info(f"Logging configured: level={log_level}, file={log_file}")


# ==================== Request/Response Logging ====================

def log_request_response(app):
    """Add request/response logging middleware.
    
    Args:
        app: Flask application instance.
    """
    
    @app.before_request
    def log_request():
        """Log incoming request details."""
        logger.info(
            f"Request: {request.method} {request.path}",
            extra={
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr,
                "user_agent": request.user_agent.string,
            }
        )
    
    @app.after_request
    def log_response(response):
        """Log outgoing response details."""
        logger.info(
            f"Response: {response.status_code}",
            extra={
                "status_code": response.status_code,
                "content_length": response.content_length,
            }
        )
        return response
