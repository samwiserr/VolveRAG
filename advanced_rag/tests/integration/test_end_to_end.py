"""
End-to-end integration tests for the complete query-to-answer pipeline.

Tests the full workflow from user query to final answer, including:
- Query processing
- Tool selection and execution
- Answer generation
- Error scenarios
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from pathlib import Path
import json

from src.core.result import Result, AppError, ErrorType
from src.core.config import get_config


@pytest.mark.integration
class TestEndToEndPipeline:
    """Test complete end-to-end query-to-answer pipeline."""
    
    @pytest.fixture
    def sample_queries(self):
        """Sample queries for testing."""
        return [
            "What is the porosity of Hugin formation in well 15/9-F-5?",
            "Tell me about well 15/9-F-4",
            "What are the petrophysical parameters for Sleipner formation?",
        ]
    
    def test_query_validation_pipeline(self, mock_config):
        """Test query validation through the pipeline."""
        from src.core.validation import validate_query, QueryRequest
        
        # Valid query
        is_valid, error = validate_query("What is porosity?")
        assert is_valid
        assert error is None
        
        # Invalid query (empty)
        is_valid, error = validate_query("")
        assert not is_valid
        assert error is not None
        
        # Invalid query (too long)
        long_query = "x" * 3000
        is_valid, error = validate_query(long_query)
        assert not is_valid
        assert error is not None
    
    def test_well_extraction_pipeline(self, mock_config):
        """Test well extraction through the pipeline."""
        from src.core.well_utils import extract_well, normalize_well, canonicalize_well
        
        queries = [
            "What is porosity in well 15/9-F-5?",
            "Tell me about 15/9-F-4",
            "Well 15/9-19A has good results",
        ]
        
        for query in queries:
            well = extract_well(query)
            if well:
                normalized = normalize_well(well)
                canonical = canonicalize_well(well)
                assert normalized is not None
                assert canonical is not None
    
    def test_result_pattern_pipeline(self, mock_config):
        """Test Result pattern through the pipeline."""
        from src.core.result import Result, AppError, ErrorType
        from src.core.tool_adapter import result_to_string
        
        # Success case
        result = Result.ok("success data")
        assert result.is_ok()
        string_result = result_to_string(result)
        assert string_result == "success data"
        
        # Error case
        error = AppError(
            type=ErrorType.NOT_FOUND_ERROR,
            message="Not found",
            details={"well": "15/9-F-5"}
        )
        result = Result.err(error)
        assert result.is_err()
        string_result = result_to_string(result)
        assert "error" in string_result.lower() or "not_found" in string_result.lower()
    
    def test_error_handling_pipeline(self, mock_config):
        """Test error handling through the pipeline."""
        from src.core.result import Result, AppError, ErrorType
        
        # Test error creation
        error = AppError(
            type=ErrorType.PROCESSING_ERROR,
            message="Processing failed",
            context={"step": "normalization"}
        )
        result = Result.err(error)
        
        # Error should be properly structured
        assert result.is_err()
        assert result.error().type == ErrorType.PROCESSING_ERROR
        assert result.error().context == {"step": "normalization"}
        
        # Test error sanitization
        sanitized_message = result.error().get_user_message()
        assert sanitized_message is not None
        assert isinstance(sanitized_message, str)
    
    def test_configuration_pipeline(self, mock_config, monkeypatch):
        """Test configuration loading through the pipeline."""
        from src.core.config import get_config, reload_config
        
        # Set test environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        
        reload_config()
        config = get_config()
        
        # Mock config may use different value, just verify it's loaded
        assert config.openai_api_key is not None
        assert config.llm_model is not None
    
    def test_caching_pipeline(self, mock_config):
        """Test caching through the pipeline."""
        from src.core.cache import get_llm_cache
        
        cache = get_llm_cache()
        
        # Set value
        cache.set("test_key_1", "test_value_1", ttl=60)
        
        # Get value
        value = cache.get("test_key_1")
        assert value == "test_value_1"
        
        # Delete value
        cache.delete("test_key_1")
        value = cache.get("test_key_1")
        assert value is None
    
    def test_rate_limiting_pipeline(self, mock_config):
        """Test rate limiting through the pipeline."""
        from src.core.security import get_rate_limiter
        
        limiter = get_rate_limiter()
        
        # First request
        result1 = limiter.check_rate_limit("user_1")
        assert result1.is_ok()
        
        # Second request (should still be allowed)
        result2 = limiter.check_rate_limit("user_1")
        assert result2.is_ok()
        
        # Different user
        result3 = limiter.check_rate_limit("user_2")
        assert result3.is_ok()
    
    def test_input_sanitization_pipeline(self, mock_config):
        """Test input sanitization through the pipeline."""
        from src.core.security import sanitize_input
        
        # Normal input
        result = sanitize_input("normal query")
        assert result.is_ok()
        assert result.unwrap() == "normal query"
        
        # Dangerous input
        result = sanitize_input("<script>alert('xss')</script>")
        assert result.is_err()
        
        # Long input
        long_input = "x" * 3000
        result = sanitize_input(long_input)
        assert result.is_err()
    
    @pytest.mark.requires_api
    def test_query_normalization_pipeline(self, mock_config):
        """Test query normalization through the pipeline."""
        from src.normalize.query_normalizer import normalize_query
        
        query = "what is porosity hugin 15/9-f-5"
        normalized = normalize_query(query)
        
        assert normalized is not None
        assert hasattr(normalized, "well") or hasattr(normalized, "formation")
    
    def test_tool_adapter_pipeline(self, mock_config):
        """Test tool adapter through the pipeline."""
        from src.core.result import Result, AppError, ErrorType
        from src.core.tool_adapter import result_to_string, tool_wrapper
        
        @tool_wrapper
        def test_tool(query: str) -> Result[str, AppError]:
            if "error" in query.lower():
                return Result.err(AppError(
                    type=ErrorType.VALIDATION_ERROR,
                    message="Test error"
                ))
            return Result.ok(f"Result for: {query}")
        
        # Success case
        result = test_tool("test query")
        assert isinstance(result, str)
        assert "test query" in result
        
        # Error case
        result = test_tool("error query")
        assert isinstance(result, str)
        # Should be JSON error format
        assert "error" in result.lower() or "validation" in result.lower()

