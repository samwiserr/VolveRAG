"""
Property-based tests for well name normalization.

Uses Hypothesis to test properties like idempotency,
normalization consistency, and edge cases.
"""
import pytest
from hypothesis import given, strategies as st, assume, settings
from src.core.well_utils import normalize_well, extract_well, canonicalize_well, strip_well_suffixes, match_well_fuzzy


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
        """Normalized well names should be uppercase or empty."""
        normalized = normalize_well(well_name)
        # Normalized should be uppercase alphanumeric only, or empty
        assert normalized.isupper() or normalized == "" or normalized.isdigit(), \
            f"Normalized name not uppercase: {normalized} (from {well_name})"
    
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
    
    @given(st.text(min_size=1, max_size=50))
    def test_canonicalize_well_returns_string(self, well_name):
        """canonicalize_well should always return a string."""
        canonical = canonicalize_well(well_name)
        assert isinstance(canonical, str), \
            f"canonicalize_well returned non-string: {type(canonical)}"
    
    @given(st.text(min_size=1, max_size=50))
    def test_canonicalize_well_is_idempotent(self, well_name):
        """canonicalize_well should be idempotent."""
        canonical_once = canonicalize_well(well_name)
        canonical_twice = canonicalize_well(canonical_once)
        
        assert canonical_once == canonical_twice, \
            f"Canonicalization not idempotent: {well_name} -> {canonical_once} -> {canonical_twice}"
    
    @given(st.text(min_size=1, max_size=50), st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
    def test_strip_well_suffixes_returns_string(self, well_name, suffixes):
        """strip_well_suffixes should always return a string."""
        result = strip_well_suffixes(well_name, suffixes)
        assert isinstance(result, str), \
            f"strip_well_suffixes returned non-string: {type(result)}"
        # Result should be shorter or equal to original
        assert len(result) <= len(well_name), \
            f"strip_well_suffixes returned longer string: {well_name} -> {result}"
    
    @given(
        st.text(min_size=1, max_size=50),
        st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5),
        st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=20)  # Limit examples to avoid slow fuzzy matching
    def test_match_well_fuzzy_returns_string_or_none(self, query_well, candidate_wells, threshold):
        """match_well_fuzzy should return string or None."""
        result = match_well_fuzzy(query_well, candidate_wells, threshold)
        assert result is None or isinstance(result, str), \
            f"match_well_fuzzy returned unexpected type: {type(result)}"
        # If result is not None, it should be in candidate_wells
        if result is not None:
            assert result in candidate_wells, \
                f"match_well_fuzzy returned well not in candidates: {result}"

