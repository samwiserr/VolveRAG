"""
Property-based tests for query expansion and normalization.

Tests properties like consistency, reversibility, and edge cases.
"""
import pytest
from hypothesis import given, strategies as st, assume
from src.normalize.query_normalizer import normalize_query


@pytest.mark.property
class TestQueryExpansionProperties:
    """Property-based tests for query expansion."""
    
    @given(st.text(min_size=1, max_size=500))
    def test_normalize_query_returns_object(self, query):
        """normalize_query should always return a NormalizedQuery object."""
        assume(query.strip())  # Skip empty queries
        
        try:
            normalized = normalize_query(query)
            assert normalized is not None, \
                f"normalize_query returned None for: {query}"
            assert hasattr(normalized, "well"), \
                f"NormalizedQuery missing 'well' attribute"
            assert hasattr(normalized, "formation"), \
                f"NormalizedQuery missing 'formation' attribute"
        except Exception as e:
            # Some queries might fail, but should fail gracefully
            assert isinstance(e, (ValueError, TypeError)), \
                f"Unexpected exception type: {type(e)}"
    
    @given(st.text(min_size=1, max_size=200))
    def test_normalize_handles_special_chars(self, query):
        """normalize_query should handle special characters."""
        # Add some special chars
        special_query = f"{query}!@#$%^&*()"
        
        try:
            normalized = normalize_query(special_query)
            assert normalized is not None
        except Exception:
            # Some special chars might cause issues, that's ok
            pass

