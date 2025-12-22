"""
Unit tests for Result monad.
"""
import pytest
from src.core.result import Result, AppError, ErrorType, sanitize_error_message


@pytest.mark.unit
class TestResult:
    """Test Result monad operations."""
    
    def test_ok_creates_success_result(self):
        """Test Result.ok() creates successful result."""
        result = Result.ok(42)
        assert result.is_ok()
        assert not result.is_err()
        assert result.unwrap() == 42
    
    def test_err_creates_error_result(self):
        """Test Result.err() creates error result."""
        error = AppError(ErrorType.VALIDATION_ERROR, "Invalid input")
        result = Result.err(error)
        assert result.is_err()
        assert not result.is_ok()
        assert result.error() == error
    
    def test_unwrap_or_returns_default_on_error(self):
        """Test unwrap_or() returns default for errors."""
        error = AppError(ErrorType.NOT_FOUND_ERROR, "Not found")
        result = Result.err(error)
        assert result.unwrap_or(100) == 100
    
    def test_unwrap_or_returns_value_on_success(self):
        """Test unwrap_or() returns value for success."""
        result = Result.ok(42)
        assert result.unwrap_or(100) == 42
    
    def test_map_applies_function_to_value(self):
        """Test map() applies function to successful value."""
        result = Result.ok(5)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_ok()
        assert mapped.unwrap() == 10
    
    def test_map_preserves_error(self):
        """Test map() preserves error."""
        error = AppError(ErrorType.PROCESSING_ERROR, "Error")
        result = Result.err(error)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_err()
        assert mapped.error() == error
    
    def test_map_handles_exceptions(self):
        """Test map() converts exceptions to errors."""
        result = Result.ok(5)
        mapped = result.map(lambda x: x / 0)  # Will raise ZeroDivisionError
        assert mapped.is_err()
        assert mapped.error().type == ErrorType.PROCESSING_ERROR
    
    def test_and_then_chains_operations(self):
        """Test and_then() chains Result-returning functions."""
        result = Result.ok(5)
        chained = result.and_then(lambda x: Result.ok(x * 2))
        assert chained.is_ok()
        assert chained.unwrap() == 10
    
    def test_and_then_preserves_error(self):
        """Test and_then() preserves error."""
        error = AppError(ErrorType.NOT_FOUND_ERROR, "Not found")
        result = Result.err(error)
        chained = result.and_then(lambda x: Result.ok(x * 2))
        assert chained.is_err()
        assert chained.error() == error
    
    def test_from_exception_converts_exception(self):
        """Test from_exception() converts exception to Result."""
        exc = ValueError("Invalid value")
        result = Result.from_exception(exc, ErrorType.VALIDATION_ERROR)
        assert result.is_err()
        assert result.error().type == ErrorType.VALIDATION_ERROR
        assert result.error().original_error == exc
    
    def test_equality(self):
        """Test Result equality comparison."""
        result1 = Result.ok(42)
        result2 = Result.ok(42)
        result3 = Result.ok(100)
        error = AppError(ErrorType.VALIDATION_ERROR, "Error")
        result4 = Result.err(error)
        
        assert result1 == result2
        assert result1 != result3
        assert result1 != result4
    
    def test_repr(self):
        """Test Result string representation."""
        result_ok = Result.ok(42)
        assert "Result.ok" in repr(result_ok)
        assert "42" in repr(result_ok)
        
        error = AppError(ErrorType.VALIDATION_ERROR, "Error")
        result_err = Result.err(error)
        assert "Result.err" in repr(result_err)


@pytest.mark.unit
class TestAppError:
    """Test AppError dataclass."""
    
    def test_error_creation(self):
        """Test AppError creation."""
        error = AppError(
            type=ErrorType.VALIDATION_ERROR,
            message="Invalid input",
            details={"field": "query"},
            context={"user_id": "123"}
        )
        assert error.type == ErrorType.VALIDATION_ERROR
        assert error.message == "Invalid input"
        assert error.details == {"field": "query"}
        assert error.context == {"user_id": "123"}
    
    def test_error_to_dict(self):
        """Test error serialization."""
        error = AppError(
            type=ErrorType.NOT_FOUND_ERROR,
            message="Not found",
            details={"well": "15/9-F-5"}
        )
        error_dict = error.to_dict()
        assert error_dict["type"] == "not_found_error"
        assert error_dict["message"] == "Not found"
        assert error_dict["details"] == {"well": "15/9-F-5"}
    
    def test_error_str(self):
        """Test error string representation."""
        error = AppError(
            type=ErrorType.VALIDATION_ERROR,
            message="Invalid input",
            context={"field": "query"}
        )
        error_str = str(error)
        assert "[validation_error]" in error_str
        assert "Invalid input" in error_str
        assert "context" in error_str
    
    def test_error_to_user_dict(self):
        """Test error serialization for user-facing responses (sanitized)."""
        error = AppError(
            type=ErrorType.PROCESSING_ERROR,
            message="Error in C:\\Users\\test\\file.py: Invalid operation",
            details={"path": "C:\\Users\\test\\file.py", "api_key": "sk-1234567890abcdef"}
        )
        user_dict = error.to_user_dict()
        assert user_dict["type"] == "processing_error"
        assert "[FILE_PATH]" in user_dict["message"]
        assert "C:\\Users" not in user_dict["message"]
        assert "[FILE_PATH]" in user_dict["details"]["path"]
        assert "[API_KEY]" in user_dict["details"]["api_key"]
    
    def test_error_get_user_message(self):
        """Test getting sanitized user-facing error message."""
        error = AppError(
            type=ErrorType.PROCESSING_ERROR,
            message="Error in /home/user/file.py: Invalid operation"
        )
        user_message = error.get_user_message()
        assert "[FILE_PATH]" in user_message
        assert "/home/user" not in user_message


@pytest.mark.unit
class TestErrorSanitization:
    """Test error message sanitization."""
    
    def test_sanitize_removes_file_paths_windows(self):
        """Test sanitization removes Windows file paths."""
        message = "Error in C:\\Users\\test\\file.py: Invalid operation"
        sanitized = sanitize_error_message(message)
        assert "[FILE_PATH]" in sanitized
        assert "C:\\Users" not in sanitized
    
    def test_sanitize_removes_file_paths_unix(self):
        """Test sanitization removes Unix file paths."""
        message = "Error in /home/user/file.py: Invalid operation"
        sanitized = sanitize_error_message(message)
        assert "[FILE_PATH]" in sanitized
        assert "/home/user" not in sanitized
    
    def test_sanitize_removes_api_keys(self):
        """Test sanitization removes API keys."""
        message = "API key sk-1234567890abcdef is invalid"
        sanitized = sanitize_error_message(message)
        assert "[API_KEY]" in sanitized
        assert "sk-1234567890abcdef" not in sanitized
    
    def test_sanitize_removes_secrets(self):
        """Test sanitization removes secrets."""
        message = "api_key=secret123 password=pass456"
        sanitized = sanitize_error_message(message)
        assert "[REDACTED]" in sanitized
        assert "secret123" not in sanitized
        assert "pass456" not in sanitized
    
    def test_sanitize_removes_email_addresses(self):
        """Test sanitization removes email addresses."""
        message = "Contact admin@example.com for help"
        sanitized = sanitize_error_message(message)
        assert "[EMAIL]" in sanitized
        assert "admin@example.com" not in sanitized
    
    def test_sanitize_removes_stack_traces(self):
        """Test sanitization removes stack traces."""
        message = "Traceback (most recent call last):\n  File \"test.py\", line 1"
        sanitized = sanitize_error_message(message)
        assert "[STACK_TRACE]" in sanitized
        assert "Traceback" not in sanitized
    
    def test_sanitize_preserves_safe_messages(self):
        """Test sanitization preserves safe error messages."""
        message = "Invalid input: query is too long"
        sanitized = sanitize_error_message(message)
        assert sanitized == message
    
    def test_sanitize_handles_empty_string(self):
        """Test sanitization handles empty strings."""
        assert sanitize_error_message("") == ""
    
    def test_sanitize_handles_none(self):
        """Test sanitization handles None."""
        assert sanitize_error_message(None) == ""

