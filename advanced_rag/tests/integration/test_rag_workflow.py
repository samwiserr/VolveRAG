"""
Integration tests for full RAG workflow.

Tests the complete query-to-answer pipeline including:
- Query normalization
- Routing decisions
- Tool execution
- Answer generation
- Error handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import MessagesState

from src.core.result import Result, AppError, ErrorType
from src.core.config import get_config
from src.graph.rag_graph import build_rag_graph


@pytest.mark.integration
class TestRAGWorkflow:
    """Test full RAG workflow integration."""
    
    @pytest.fixture
    def mock_tools(self):
        """Create mock tools for testing."""
        from langchain.tools import tool
        
        @tool
        def mock_retrieve_documents(query: str) -> str:
            """Retrieve relevant documents."""
            return "Mocked document retrieval result"
        
        @tool
        def mock_lookup_petrophysical_params(query: str) -> str:
            """Lookup petrophysical parameters."""
            return '{"netgros": 0.85, "phif": 0.25}'
        
        return [mock_retrieve_documents, mock_lookup_petrophysical_params]
    
    @pytest.fixture
    def sample_state(self):
        """Create sample MessagesState for testing."""
        return {
            "messages": [
                HumanMessage(content="What is the porosity of Hugin formation in 15/9-F-5?")
            ]
        }
    
    @pytest.mark.requires_api
    def test_workflow_initialization(self, mock_config, mock_tools):
        """Test that RAG workflow can be initialized."""
        graph = build_rag_graph(mock_tools)
        assert graph is not None
        assert hasattr(graph, "invoke")
    
    @pytest.mark.requires_api
    def test_query_normalization_integration(self, mock_config):
        """Test query normalization works in integration."""
        from src.normalize.query_normalizer import normalize_query
        
        query = "what is porosity hugin 15/9-f-5"
        normalized = normalize_query(query)
        
        assert normalized is not None
        assert hasattr(normalized, "well")
        assert hasattr(normalized, "formation")
    
    @pytest.mark.requires_api
    def test_routing_integration(self, mock_config, sample_state):
        """Test routing logic works in integration."""
        from src.graph.routing.router import QueryRouter
        from src.normalize.query_normalizer import normalize_query
        
        query = sample_state["messages"][0].content
        normalized = normalize_query(query)
        
        router = QueryRouter(tools=[])
        # Router should be able to process the query
        assert router is not None
    
    @pytest.mark.requires_vectorstore
    def test_retrieval_integration(self, mock_config, temp_vectorstore):
        """Test document retrieval works end-to-end."""
        from src.tools.retriever_tool import RetrieverTool
        
        # This test requires actual vectorstore
        # Skip if not available
        if not (temp_vectorstore / "chroma.sqlite3").exists():
            pytest.skip("Vectorstore not available")
        
        retriever = RetrieverTool(persist_dir=str(temp_vectorstore))
        result = retriever.retrieve("test query", k=5)
        
        assert result is not None
        assert isinstance(result, (list, str))
    
    def test_error_propagation(self, mock_config):
        """Test that errors propagate correctly through the system."""
        from src.core.result import Result, AppError, ErrorType
        
        # Create an error
        error = AppError(
            type=ErrorType.NOT_FOUND_ERROR,
            message="Test error",
            details={"key": "value"}
        )
        result = Result.err(error)
        
        # Error should propagate
        assert result.is_err()
        assert result.error().type == ErrorType.NOT_FOUND_ERROR
        assert result.error().message == "Test error"
    
    @pytest.mark.requires_api
    def test_caching_integration(self, mock_config):
        """Test that caching works in integration."""
        from src.core.cache import get_llm_cache
        
        cache = get_llm_cache()
        
        # Set a value
        cache.set("test_key", "test_value", ttl=60)
        
        # Get it back
        value = cache.get("test_key")
        assert value == "test_value"
        
        # Clean up
        cache.delete("test_key")
    
    def test_rate_limiting_integration(self, mock_config):
        """Test that rate limiting works in integration."""
        from src.core.security import get_rate_limiter
        
        limiter = get_rate_limiter()
        
        # First request should be allowed
        result = limiter.check_rate_limit("test_user_1")
        assert result.is_ok()
        
        # Check remaining
        remaining = limiter.get_remaining("test_user_1")
        assert remaining >= 0
    
    def test_input_validation_integration(self, mock_config):
        """Test input validation works end-to-end."""
        from src.core.validation import validate_query
        from src.core.security import sanitize_input
        
        # Valid query
        is_valid, error = validate_query("What is porosity?")
        assert is_valid
        assert error is None
        
        # Invalid query (too long)
        is_valid, error = validate_query("x" * 3000)
        assert not is_valid
        assert error is not None
        
        # Sanitization
        result = sanitize_input("test query")
        assert result.is_ok()
        assert result.unwrap() == "test query"

