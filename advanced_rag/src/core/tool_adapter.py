"""
Adapter for converting Result types to string returns for LangChain tools.

LangChain tools must return strings, but we want to use Result pattern
internally. This adapter bridges the gap.
"""
from typing import Callable, TypeVar
from .result import Result, AppError, ErrorType

T = TypeVar('T')


def result_to_string(result: Result[str, AppError], default_error: str = "An error occurred") -> str:
    """
    Convert Result to string for LangChain tool compatibility.
    
    Sanitizes error messages to remove sensitive information (file paths, secrets)
    before returning to users.
    
    Args:
        result: Result containing string or error
        default_error: Default error message if result is error
        
    Returns:
        String value or formatted error message (sanitized)
    """
    if result.is_ok():
        return result.unwrap()
    else:
        error = result.error()
        # Use sanitized user-facing error information
        # Maintain backward compatibility with "error" key for existing tests
        error_dict = error.to_user_dict()
        # Add "error" key for backward compatibility
        error_dict["error"] = error_dict["type"]
        
        import json
        return json.dumps(error_dict, ensure_ascii=False)


def tool_wrapper(func: Callable[..., Result[str, AppError]]) -> Callable[..., str]:
    """
    Decorator to wrap a Result-returning function for LangChain tool compatibility.
    
    Args:
        func: Function that returns Result[str, AppError]
        
    Returns:
        Function that returns str (for LangChain)
    """
    def wrapper(*args, **kwargs) -> str:
        result = func(*args, **kwargs)
        return result_to_string(result)
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper

