"""
Structured logging setup for VolveRAG.

This module provides structured JSON logging that works well with both
CLI and Streamlit applications, while maintaining backward compatibility.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from .config import get_config, LogLevel


class StructuredFormatter(logging.Formatter):
    """
    JSON structured formatter for better log aggregation and analysis.
    
    Formats log records as JSON with consistent structure including
    timestamp, level, logger name, message, and optional context.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON string representation
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra context if present
        if hasattr(record, "context") and record.context:
            log_data["context"] = record.context
        
        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info",
                "context"
            ]:
                log_data[key] = value
        
        return json.dumps(log_data, default=str, ensure_ascii=False)


class StreamlitCompatibleFormatter(logging.Formatter):
    """
    Formatter that works well with Streamlit's logging display.
    
    Uses a readable text format that Streamlit can display nicely,
    while still including structured information.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record for Streamlit display.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted string
        """
        # Base format
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname
        logger_name = record.name.split('.')[-1]  # Just the module name
        message = record.getMessage()
        
        formatted = f"[{timestamp}] {level} - {logger_name} - {message}"
        
        # Add context if present
        if hasattr(record, "context") and record.context:
            formatted += f" | Context: {record.context}"
        
        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


def setup_logging(force_reload: bool = False) -> None:
    """
    Configure structured logging for the application.
    
    This function sets up logging based on configuration, with support
    for both JSON (for production/log aggregation) and text (for development/Streamlit)
    formats.
    
    Args:
        force_reload: Force reconfiguration even if already configured
    """
    # Check if already configured (unless forcing)
    root_logger = logging.getLogger()
    if root_logger.handlers and not force_reload:
        return
    
    try:
        config = get_config()
        log_format = config.log_format
        log_level = getattr(logging, config.log_level.value, logging.INFO)
    except Exception:
        # Fallback if config not available
        log_format = "text"
        log_level = logging.INFO
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler()
    
    # Set formatter based on config
    if log_format == "json":
        handler.setFormatter(StructuredFormatter())
    else:
        # Use Streamlit-compatible formatter for text mode
        handler.setFormatter(StreamlitCompatibleFormatter())
    
    # Set level
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    
    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False


def log_with_context(
    logger: logging.Logger,
    level: int,
    message: str,
    **context: Any
) -> None:
    """
    Log message with additional context.
    
    This helper function makes it easy to add structured context to log messages,
    which is especially useful for debugging and monitoring.
    
    Args:
        logger: Logger instance
        level: Log level (logging.INFO, logging.ERROR, etc.)
        message: Log message
        **context: Additional context as keyword arguments
    """
    extra = {"context": context}
    logger.log(level, message, extra=extra)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance with proper configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    # Ensure logging is set up
    setup_logging()
    return logging.getLogger(name)

