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
from .config import get_config, reload_config, reset_config, AppConfig
from .path_resolver import PathResolver
from .logging import setup_logging, get_logger, log_with_context
from .container import ServiceContainer, get_container, reset_container
from .well_utils import extract_well, normalize_well, canonicalize_well, strip_well_suffixes, match_well_fuzzy
from .validation import QueryRequest, WellNameRequest, FormationRequest, validate_query
from .thresholds import MatchingThresholds, RetrievalThresholds, get_matching_thresholds, get_retrieval_thresholds
from .tool_adapter import result_to_string, tool_wrapper
from .cache import Cache, get_llm_cache, get_embedding_cache, cached, generate_cache_key
from .security import RateLimiter, TokenBucket, get_rate_limiter, rate_limit, sanitize_input

# Initialize logging on import (but only if not already configured)
try:
    from .logging import setup_logging
    setup_logging()
except (ImportError, AttributeError, ValueError, TypeError) as e:
    # If logging setup fails, continue with default logging
    # This ensures the app doesn't crash on import
    # Log to stderr if possible, otherwise silently continue
    import sys
    print(f"Warning: Logging setup failed: {e}", file=sys.stderr)

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
    "reset_config",
    "AppConfig",
    "PathResolver",
    "setup_logging",
    "get_logger",
    "log_with_context",
    "ServiceContainer",
    "get_container",
    "reset_container",
    "extract_well",
    "normalize_well",
    "canonicalize_well",
    "strip_well_suffixes",
    "match_well_fuzzy",
    "QueryRequest",
    "WellNameRequest",
    "FormationRequest",
    "validate_query",
    "MatchingThresholds",
    "RetrievalThresholds",
    "get_matching_thresholds",
    "get_retrieval_thresholds",
    "result_to_string",
    "tool_wrapper",
    "Cache",
    "get_llm_cache",
    "get_embedding_cache",
    "cached",
    "generate_cache_key",
    "RateLimiter",
    "TokenBucket",
    "get_rate_limiter",
    "rate_limit",
    "sanitize_input",
]
