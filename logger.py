#!/usr/bin/env python3
"""
Logging configuration for AID Commander
Provides structured logging with different levels and output formats
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class AIDLogger:
    """Custom logger for AID Commander with user-friendly output"""
    
    def __init__(self, name: str = "aid_commander", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(self.log_level)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers with appropriate formatting"""
        
        # Console handler for user-friendly output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        
        # File handler for detailed debugging
        log_dir = Path.home() / ".aid_commander" / "logs"
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Fallback to temp directory if home is not writable
            import tempfile
            log_dir = Path(tempfile.gettempdir()) / "aid_commander_logs"
            log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"aid_commander_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, emoji: str = "ℹ️"):
        """Log info message with optional emoji"""
        self.logger.info(f"{emoji} {message}")
    
    def success(self, message: str):
        """Log success message"""
        self.logger.info(f"✅ {message}")
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}")
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log error message with optional exception details"""
        error_msg = f"❌ {message}"
        if exception:
            error_msg += f"\n   Details: {str(exception)}"
        self.logger.error(error_msg)
        
        # Log full traceback to file only
        if exception:
            self.logger.debug("Full traceback:", exc_info=True)
    
    def debug(self, message: str):
        """Log debug message (file only)"""
        self.logger.debug(f"🔍 {message}")
    
    def ai_activity(self, message: str):
        """Log AI-related activity"""
        self.logger.info(f"🤖 {message}")
    
    def task_activity(self, message: str):
        """Log task-related activity"""
        self.logger.info(f"📝 {message}")
    
    def project_activity(self, message: str):
        """Log project-related activity"""
        self.logger.info(f"🎯 {message}")


class ErrorHandler:
    """Centralized error handling for AID Commander"""
    
    def __init__(self, logger: AIDLogger):
        self.logger = logger
    
    def handle_file_error(self, operation: str, file_path: Path, exception: Exception):
        """Handle file operation errors"""
        if isinstance(exception, FileNotFoundError):
            self.logger.error(f"File not found during {operation}: {file_path}")
            return f"File not found: {file_path}"
        elif isinstance(exception, PermissionError):
            self.logger.error(f"Permission denied during {operation}: {file_path}")
            return f"Permission denied: {file_path}"
        else:
            self.logger.error(f"File error during {operation}: {file_path}", exception)
            return f"File operation failed: {operation}"
    
    def handle_network_error(self, operation: str, exception: Exception):
        """Handle network/API errors"""
        if "401" in str(exception):
            self.logger.error(f"Authentication failed for {operation}")
            return "API authentication failed. Please check your API key."
        elif "403" in str(exception):
            self.logger.error(f"Access forbidden for {operation}")
            return "API access forbidden. Please check your permissions."
        elif "429" in str(exception):
            self.logger.error(f"Rate limit exceeded for {operation}")
            return "API rate limit exceeded. Please try again later."
        else:
            self.logger.error(f"Network error during {operation}", exception)
            return f"Network error: {operation} failed"
    
    def handle_config_error(self, operation: str, exception: Exception):
        """Handle configuration errors"""
        self.logger.error(f"Configuration error during {operation}", exception)
        return f"Configuration error: {operation}. Run 'aid-commander init' to reset."
    
    def handle_template_error(self, operation: str, exception: Exception):
        """Handle template processing errors"""
        self.logger.error(f"Template error during {operation}", exception)
        return f"Template processing failed: {operation}"
    
    def handle_ai_error(self, operation: str, exception: Exception):
        """Handle AI service errors"""
        if "api" in str(exception).lower():
            return self.handle_network_error(f"AI {operation}", exception)
        else:
            self.logger.error(f"AI service error during {operation}", exception)
            return f"AI service error: {operation}. Falling back to manual mode."
    
    def handle_unexpected_error(self, operation: str, exception: Exception):
        """Handle unexpected errors"""
        self.logger.error(f"Unexpected error during {operation}", exception)
        return f"Unexpected error: {operation}. Please check the logs for details."


# Global logger instance
_logger_instance = None


def get_logger() -> AIDLogger:
    """Get the global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AIDLogger()
    return _logger_instance


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return ErrorHandler(get_logger())


# Decorator for error handling
def handle_errors(operation_name: str):
    """Decorator to handle errors in functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_error_handler()
                error_message = error_handler.handle_unexpected_error(operation_name, e)
                print(error_message)
                return None
        return wrapper
    return decorator


# Usage examples
if __name__ == "__main__":
    # Test logging
    logger = get_logger()
    error_handler = get_error_handler()
    
    logger.success("AID Commander initialized successfully")
    logger.ai_activity("AI provider configured")
    logger.task_activity("Task added to project")
    logger.project_activity("New project created")
    logger.warning("Template validation found issues")
    
    # Test error handling
    try:
        raise FileNotFoundError("Test file not found")
    except Exception as e:
        message = error_handler.handle_file_error("test operation", Path("test.txt"), e)
        print(message)