"""
Backward compatibility layer for gradual migration.

This module provides compatibility functions that allow existing code
to continue working while we migrate to the new Result/Config patterns.
"""
from typing import Optional, Union, Any
from .result import Result, AppError
from .config import get_config
import os


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Backward-compatible environment variable getter.
    
    This function provides a compatibility layer for os.getenv() calls,
    while also checking the new config system. This allows gradual migration.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    # First try config (if the key exists in config)
    try:
        config = get_config()
        # Map common env vars to config attributes
        config_map = {
            "OPENAI_API_KEY": getattr(config, "openai_api_key", None),
            "OPENAI_MODEL": getattr(config, "llm_model", None).value if hasattr(config, "llm_model") else None,
            "OPENAI_GRADE_MODEL": getattr(config, "grade_model", None).value if hasattr(config, "grade_model") else None,
            "EMBEDDING_MODEL": getattr(config, "embedding_model", None).value if hasattr(config, "embedding_model") else None,
            "RAG_USE_CROSS_ENCODER": str(getattr(config, "use_cross_encoder", None)).lower() if hasattr(config, "use_cross_encoder") else None,
            "RAG_RERANK": str(getattr(config, "rerank_enabled", None)).lower() if hasattr(config, "rerank_enabled") else None,
            "RAG_RERANK_MODEL": getattr(config, "rerank_model", None).value if hasattr(config, "rerank_model") else None,
            "RAG_MMR": str(getattr(config, "mmr_enabled", None)).lower() if hasattr(config, "mmr_enabled") else None,
            "RAG_MMR_LAMBDA": str(getattr(config, "mmr_lambda", None)) if hasattr(config, "mmr_lambda") else None,
            "RAG_ENABLE_QUERY_DECOMPOSITION": str(getattr(config, "enable_query_decomposition", None)).lower() if hasattr(config, "enable_query_decomposition") else None,
            "RAG_ENABLE_QUERY_COMPLETION": str(getattr(config, "enable_query_completion", None)).lower() if hasattr(config, "enable_query_completion") else None,
            "RAG_DECOMPOSITION_MODEL": getattr(config, "decomposition_model", None).value if hasattr(config, "decomposition_model") else None,
            "RAG_ENTITY_RESOLVER": str(getattr(config, "enable_entity_resolver", None)).lower() if hasattr(config, "enable_entity_resolver") else None,
            "RAG_ENTITY_RESOLVER_MODEL": getattr(config, "entity_resolver_model", None).value if hasattr(config, "entity_resolver_model") else None,
            "VECTORSTORE_PATH": str(getattr(config, "persist_directory", None)) if hasattr(config, "persist_directory") else None,
            "DOCUMENTS_PATH": str(getattr(config, "documents_path", None)) if hasattr(config, "documents_path") and getattr(config, "documents_path") else None,
            "LOG_LEVEL": getattr(config, "log_level", None).value if hasattr(config, "log_level") else None,
            "LOG_FORMAT": getattr(config, "log_format", None) if hasattr(config, "log_format") else None,
            "VECTORSTORE_URL": getattr(config, "vectorstore_url", None) if hasattr(config, "vectorstore_url") else None,
            "PDFS_URL": getattr(config, "pdfs_url", None) if hasattr(config, "pdfs_url") else None,
        }
        
        if key in config_map and config_map[key] is not None:
            return config_map[key]
    except Exception:
        # If config fails, fall back to os.getenv
        pass
    
    # Fallback to os.getenv
    return os.getenv(key, default)


def unwrap_result(result: Union[Result[Any, AppError], Any], default: Any = None) -> Any:
    """
    Unwrap Result or return value directly (backward compatibility).
    
    This function allows code to work with both Result types and regular values,
    making migration easier.
    
    Args:
        result: Result instance or regular value
        default: Default value if Result is error
        
    Returns:
        Unwrapped value or default
    """
    if isinstance(result, Result):
        if result.is_ok():
            return result.unwrap()
        return default
    return result

