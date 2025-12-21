"""
Core module for VolveRAG - provides foundational utilities for error handling,
configuration, logging, and path resolution.
"""

from .result import Result, AppError, ErrorType
from .exceptions import (
    VolveRAGError,
    ValidationError,
    WellNotFoundError,
    FormationNotFoundError,
    CacheError,
    RetrievalError,
    LLMError,
    ConfigurationError,
)
from .compat import get_env, unwrap_result
from .config import get_config, reload_config, AppConfig
from .path_resolver import PathResolver
from .logging import setup_logging, get_logger, log_with_context

# Initialize logging on import (but only if not already configured)
try:
    from .logging import setup_logging
    setup_logging()
except Exception:
    # If logging setup fails, continue with default logging
    # This ensures the app doesn't crash on import
    pass

__all__ = [
    "Result",
    "AppError",
    "ErrorType",
    "VolveRAGError",
    "ValidationError",
    "WellNotFoundError",
    "FormationNotFoundError",
    "CacheError",
    "RetrievalError",
    "LLMError",
    "ConfigurationError",
    "get_env",
    "unwrap_result",
    "get_config",
    "reload_config",
    "AppConfig",
    "PathResolver",
    "setup_logging",
    "get_logger",
    "log_with_context",
]
