"""
Centralized Error Handler

This module provides centralized error handling for the Underwriting Dashboard application.
It includes utilities for capturing, logging, and reporting errors in a consistent manner.
"""

import logging
import traceback
import sys
import functools
import inspect
from enum import Enum
from typing import Callable, Any, Dict, Optional, Type, List, Union
from datetime import datetime
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Enumeration of error severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ApplicationError(Exception):
    """Base exception class for application errors."""
    
    def __init__(
        self, 
        message: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        cause: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the application error.
        
        Args:
            message: Error message
            severity: Error severity level
            cause: Original exception that caused this error
            details: Additional error details
        """
        self.message = message
        self.severity = severity
        self.cause = cause
        self.details = details or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
        super().__init__(message)
    
    def __str__(self) -> str:
        """String representation of the error."""
        result = f"{self.severity.value}: {self.message}"
        if self.cause:
            result += f" (Caused by: {type(self.cause).__name__}: {str(self.cause)})"
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to a dictionary for serialization."""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "cause": str(self.cause) if self.cause else None,
            "cause_type": type(self.cause).__name__ if self.cause else None,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback
        }

class DataError(ApplicationError):
    """Error related to data processing or validation."""
    pass

class DatabaseError(ApplicationError):
    """Error related to database operations."""
    pass

class FileError(ApplicationError):
    """Error related to file operations."""
    pass

class ConfigError(ApplicationError):
    """Error related to configuration issues."""
    pass

class NetworkError(ApplicationError):
    """Error related to network operations."""
    pass

def handle_error(
    error: Exception,
    default_return: Any = None,
    error_type: Type[ApplicationError] = ApplicationError,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    log_error: bool = True,
    raise_error: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Handle an exception in a standardized way.
    
    Args:
        error: The exception to handle
        default_return: Value to return if the error is not raised
        error_type: Type of ApplicationError to create
        severity: Error severity level
        log_error: Whether to log the error
        raise_error: Whether to raise the wrapped error
        context: Additional context information
        
    Returns:
        The default_return value if not raising
        
    Raises:
        ApplicationError: If raise_error is True
    """
    # Create application error
    app_error = error_type(
        message=str(error),
        severity=severity,
        cause=error,
        details=context
    )
    
    # Log the error if requested
    if log_error:
        log_message = f"{app_error}"
        if context:
            log_message += f" Context: {context}"
        
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=error)
        elif severity == ErrorSeverity.ERROR:
            logger.error(log_message, exc_info=error)
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message, exc_info=error)
        else:
            logger.info(log_message, exc_info=error)
    
    # Raise or return
    if raise_error:
        raise app_error
    
    return default_return

def error_handler(
    error_type: Type[ApplicationError] = ApplicationError,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    default_return: Any = None,
    log_error: bool = True,
    raise_error: bool = False
) -> Callable:
    """
    Decorator to handle errors in a function.
    
    Args:
        error_type: Type of ApplicationError to create
        severity: Error severity level
        default_return: Value to return if an error occurs
        log_error: Whether to log the error
        raise_error: Whether to raise the wrapped error
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get context information
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                return handle_error(
                    error=e,
                    default_return=default_return,
                    error_type=error_type,
                    severity=severity,
                    log_error=log_error,
                    raise_error=raise_error,
                    context=context
                )
        return wrapper
    return decorator

class ErrorRegistry:
    """Registry for tracking application errors."""
    
    def __init__(self, max_errors: int = 100):
        """
        Initialize the error registry.
        
        Args:
            max_errors: Maximum number of errors to keep in memory
        """
        self.errors: List[ApplicationError] = []
        self.max_errors = max_errors
    
    def register(self, error: ApplicationError) -> None:
        """
        Register an error in the registry.
        
        Args:
            error: The error to register
        """
        self.errors.append(error)
        
        # Trim the list if it gets too long
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors:]
    
    def get_errors(
        self, 
        severity: Optional[ErrorSeverity] = None,
        error_type: Optional[Type[ApplicationError]] = None,
        limit: int = 50
    ) -> List[ApplicationError]:
        """
        Get errors from the registry, optionally filtered.
        
        Args:
            severity: Filter by severity level
            error_type: Filter by error type
            limit: Maximum number of errors to return
            
        Returns:
            List of matching errors
        """
        filtered = self.errors
        
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        
        if error_type:
            filtered = [e for e in filtered if isinstance(e, error_type)]
        
        # Return the most recent errors first
        return list(reversed(filtered))[-limit:]
    
    def clear(self) -> None:
        """Clear all errors from the registry."""
        self.errors = []
    
    def export_to_log(self, log_file: Path) -> None:
        """
        Export all errors to a log file.
        
        Args:
            log_file: Path to the log file
        """
        with open(log_file, 'a') as f:
            f.write(f"\n--- Error export {datetime.now().isoformat()} ---\n")
            for error in self.errors:
                f.write(f"{error.timestamp.isoformat()} - {error}\n")
                if error.traceback:
                    f.write(f"Traceback:\n{error.traceback}\n")
                f.write("\n")

# Create a global error registry
error_registry = ErrorRegistry()

# Function to register an error
def register_error(error: ApplicationError) -> None:
    """
    Register an error in the global registry.
    
    Args:
        error: The error to register
    """
    error_registry.register(error)

# Enhanced error handler that also registers errors
def capture_error(
    error: Exception,
    default_return: Any = None,
    error_type: Type[ApplicationError] = ApplicationError,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    log_error: bool = True,
    raise_error: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Handle and register an exception.
    
    Args:
        error: The exception to handle
        default_return: Value to return if the error is not raised
        error_type: Type of ApplicationError to create
        severity: Error severity level
        log_error: Whether to log the error
        raise_error: Whether to raise the wrapped error
        context: Additional context information
        
    Returns:
        The default_return value if not raising
        
    Raises:
        ApplicationError: If raise_error is True
    """
    # Create application error
    app_error = error_type(
        message=str(error),
        severity=severity,
        cause=error,
        details=context
    )
    
    # Register the error
    register_error(app_error)
    
    # Log the error if requested
    if log_error:
        log_message = f"{app_error}"
        if context:
            log_message += f" Context: {context}"
        
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=error)
        elif severity == ErrorSeverity.ERROR:
            logger.error(log_message, exc_info=error)
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message, exc_info=error)
        else:
            logger.info(log_message, exc_info=error)
    
    # Raise or return
    if raise_error:
        raise app_error
    
    return default_return

# Enhanced decorator that registers errors
def capture_errors(
    error_type: Type[ApplicationError] = ApplicationError,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    default_return: Any = None,
    log_error: bool = True,
    raise_error: bool = False
) -> Callable:
    """
    Decorator to handle and register errors in a function.
    
    Args:
        error_type: Type of ApplicationError to create
        severity: Error severity level
        default_return: Value to return if an error occurs
        log_error: Whether to log the error
        raise_error: Whether to raise the wrapped error
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get context information
                context = {
                    "function": func.__name__,
                    "module": func.__module__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                return capture_error(
                    error=e,
                    default_return=default_return,
                    error_type=error_type,
                    severity=severity,
                    log_error=log_error,
                    raise_error=raise_error,
                    context=context
                )
        return wrapper
    return decorator