"""
Domain-specific exceptions for VolveRAG.

These exceptions provide more specific error types than generic Exception,
making error handling more precise and user-friendly.
"""


class VolveRAGError(Exception):
    """Base exception for all VolveRAG errors."""
    pass


class ValidationError(VolveRAGError):
    """Input validation failed."""
    pass


class WellNotFoundError(VolveRAGError):
    """Well not found in dataset."""
    pass


class FormationNotFoundError(VolveRAGError):
    """Formation not found for well."""
    pass


class CacheError(VolveRAGError):
    """Cache operation failed."""
    pass


class RetrievalError(VolveRAGError):
    """Document retrieval failed."""
    pass


class LLMError(VolveRAGError):
    """LLM API call failed."""
    pass


class ConfigurationError(VolveRAGError):
    """Configuration error."""
    pass

