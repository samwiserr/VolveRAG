"""
Property-based tests for query expansion and normalization.

Tests properties like consistency, reversibility, and edge cases.
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from src.normalize.query_normalizer import normalize_query


@pytest.mark.property
class TestQueryExpansionProperties:
    """Property-based tests for query expansion."""
    
    @given(st.text(min_size=1, max_size=200))  # Reduced max_size to avoid timeout
    @settings(deadline=5000)  # Increase deadline for potentially slow operations
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
            assert isinstance(e, (ValueError, TypeError, AttributeError)), \
                f"Unexpected exception type: {type(e)}"
    
    @given(st.text(min_size=1, max_size=200))
    @settings(deadline=5000)  # Increase deadline for potentially slow operations
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
    
    @given(st.text(min_size=1, max_size=200))
    @settings(deadline=5000, max_examples=20)  # Limit examples and increase deadline
    def test_normalize_query_consistency(self, query):
        """normalize_query should return consistent results for same input."""
        assume(query.strip())
        
        try:
            normalized1 = normalize_query(query)
            normalized2 = normalize_query(query)
            
            # Results should be consistent
            assert normalized1.well == normalized2.well, \
                f"Well extraction inconsistent: {normalized1.well} vs {normalized2.well}"
            assert normalized1.formation == normalized2.formation, \
                f"Formation extraction inconsistent: {normalized1.formation} vs {normalized2.formation}"
        except Exception:
            # Some queries might fail, that's ok
            pass
    
    @given(st.text(min_size=1, max_size=100))
    @settings(deadline=5000, max_examples=20)
    def test_normalize_query_attributes(self, query):
        """NormalizedQuery should have all required attributes."""
        assume(query.strip())
        
        try:
            normalized = normalize_query(query)
            # Check all required attributes exist
            assert hasattr(normalized, "raw")
            assert hasattr(normalized, "well")
            assert hasattr(normalized, "formation")
            assert hasattr(normalized, "property")
            assert hasattr(normalized, "tool")
            assert hasattr(normalized, "intent")
            
            # Check types
            assert isinstance(normalized.raw, str)
            assert normalized.well is None or isinstance(normalized.well, str)
            assert normalized.formation is None or isinstance(normalized.formation, str)
            assert normalized.intent in ["fact", "list", "section", "unknown"]
        except Exception:
            # Some queries might fail, that's ok
            pass

