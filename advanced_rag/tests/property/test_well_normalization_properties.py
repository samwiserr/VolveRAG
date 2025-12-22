"""
Property-based tests for well name normalization.

Uses Hypothesis to test properties like idempotency,
normalization consistency, and edge cases.
"""
import pytest
from hypothesis import given, strategies as st, assume
from src.core.well_utils import normalize_well, extract_well


@pytest.mark.property
class TestWellNormalizationProperties:
    """Property-based tests for well normalization."""
    
    @given(st.text(min_size=1, max_size=50))
    def test_normalize_is_idempotent(self, well_name):
        """Normalization should be idempotent (applying twice gives same result)."""
        assume(well_name.strip())  # Skip empty strings after strip
        
        normalized_once = normalize_well(well_name)
        normalized_twice = normalize_well(normalized_once)
        
        assert normalized_once == normalized_twice, \
            f"Normalization not idempotent: {well_name} -> {normalized_once} -> {normalized_twice}"
    
    @given(st.text(min_size=1, max_size=50))
    def test_normalize_is_uppercase(self, well_name):
        """Normalized well names should be uppercase."""
        normalized = normalize_well(well_name)
        assert normalized.isupper() or normalized == "", \
            f"Normalized name not uppercase: {normalized}"
    
    @given(st.text(min_size=5, max_size=100))
    def test_extract_well_returns_string_or_none(self, text):
        """extract_well should return string or None."""
        result = extract_well(text)
        assert result is None or isinstance(result, str), \
            f"extract_well returned unexpected type: {type(result)}"
    
    @given(
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=20)
    )
    def test_normalize_handles_variations(self, prefix, suffix):
        """Normalization should handle various prefixes and suffixes."""
        well = f"{prefix}15/9-F-5{suffix}"
        normalized = normalize_well(well)
        
        # Should contain the core well identifier
        assert "159F5" in normalized or "15" in normalized, \
            f"Normalization lost core identifier: {well} -> {normalized}"

