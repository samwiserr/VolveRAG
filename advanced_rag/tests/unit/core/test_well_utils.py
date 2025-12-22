"""
Unit tests for well_utils module.
"""
import pytest
from src.core.well_utils import (
    extract_well,
    normalize_well,
    canonicalize_well,
    strip_well_suffixes,
    match_well_fuzzy
)


@pytest.mark.unit
class TestExtractWell:
    """Test extract_well function."""
    
    def test_extracts_well_from_text(self):
        """Test extracts well name from text."""
        text = "Well 15/9-F-5 has good results"
        result = extract_well(text)
        assert result is not None
        assert "15/9-F-5" in result or "15/9-F5" in result
    
    def test_returns_none_when_no_well(self):
        """Test returns None when no well found."""
        text = "This text has no well name"
        result = extract_well(text)
        # May return None or empty string depending on implementation
        assert result is None or result == ""
    
    def test_handles_various_formats(self):
        """Test handles various well name formats."""
        formats = [
            "15/9-F-5",
            "15/9-F5",
            "15_9_F_5",
            "15-9-F-5",
        ]
        for fmt in formats:
            result = extract_well(f"Query about well {fmt}")
            assert result is not None


@pytest.mark.unit
class TestNormalizeWell:
    """Test normalize_well function."""
    
    def test_normalizes_standard_format(self):
        """Test normalizes standard well format."""
        assert normalize_well("15/9-F-5") == "159F5"
        assert normalize_well("15/9-F5") == "159F5"
    
    def test_handles_uppercase(self):
        """Test handles uppercase input."""
        assert normalize_well("15/9-f-5") == "159F5"
    
    def test_removes_all_non_alphanumeric(self):
        """Test removes all non-alphanumeric characters."""
        assert normalize_well("15/9-F-5 A") == "159F5A"
        assert normalize_well("15_9_F_5") == "159F5"
    
    def test_handles_empty_string(self):
        """Test handles empty string."""
        assert normalize_well("") == ""
    
    def test_handles_whitespace(self):
        """Test handles whitespace."""
        assert normalize_well(" 15/9-F-5 ") == "159F5"


@pytest.mark.unit
class TestCanonicalizeWell:
    """Test canonicalize_well function."""
    
    def test_canonicalizes_standard_format(self):
        """Test canonicalizes to standard format."""
        result = canonicalize_well("15/9-F-5")
        assert "15/9" in result
        assert "F" in result
    
    def test_handles_variations(self):
        """Test handles various input formats."""
        variations = ["15/9-F5", "15_9_F_5", "15-9-F-5"]
        for var in variations:
            result = canonicalize_well(var)
            assert result is not None
            assert len(result) > 0


@pytest.mark.unit
class TestStripWellSuffixes:
    """Test strip_well_suffixes function."""
    
    def test_strips_default_suffixes(self):
        """Test strips default suffixes."""
        assert strip_well_suffixes("159F5PETROPHYSICAL") == "159F5"
        assert strip_well_suffixes("159F5FORMATION") == "159F5"
        assert strip_well_suffixes("159F5REPORT") == "159F5"
    
    def test_strips_custom_suffixes(self):
        """Test strips custom suffixes."""
        assert strip_well_suffixes("159F5CUSTOM", ["CUSTOM"]) == "159F5"
    
    def test_strips_only_first_matching_suffix(self):
        """Test strips only first matching suffix."""
        # The function checks suffixes in order, so "FORMATION" comes before "PETROPHYSICAL"
        # and will be stripped first if the string ends with it
        result = strip_well_suffixes("159F5FORMATION")
        assert result == "159F5"  # Only first matching suffix removed
        
        # Test with PETROPHYSICAL at the end
        result2 = strip_well_suffixes("159F5PETROPHYSICAL")
        assert result2 == "159F5"
    
    def test_returns_unchanged_if_no_suffix(self):
        """Test returns unchanged if no suffix matches."""
        assert strip_well_suffixes("159F5") == "159F5"
    
    def test_handles_empty_string(self):
        """Test handles empty string."""
        assert strip_well_suffixes("") == ""
    
    def test_handles_none_suffixes(self):
        """Test handles None suffixes (uses defaults)."""
        assert strip_well_suffixes("159F5PETROPHYSICAL", None) == "159F5"


@pytest.mark.unit
class TestMatchWellFuzzy:
    """Test match_well_fuzzy function."""
    
    def test_matches_exact_well(self):
        """Test matches exact well name."""
        candidates = ["15/9-F-5", "15/9-F-4", "15/9-F-6"]
        result = match_well_fuzzy("15/9-F-5", candidates)
        assert result == "15/9-F-5"
    
    def test_matches_similar_well(self):
        """Test matches similar well name."""
        candidates = ["15/9-F-5", "15/9-F-4", "15/9-F-6"]
        result = match_well_fuzzy("15/9-F5", candidates)  # Missing dash
        assert result is not None
        assert result in candidates
    
    def test_returns_none_below_threshold(self):
        """Test returns None when similarity below threshold."""
        candidates = ["15/9-F-5", "15/9-F-4"]
        result = match_well_fuzzy("99/9-X-99", candidates, threshold=0.95)
        assert result is None
    
    def test_handles_empty_candidates(self):
        """Test handles empty candidate list."""
        result = match_well_fuzzy("15/9-F-5", [])
        assert result is None
    
    def test_handles_single_candidate(self):
        """Test handles single candidate."""
        candidates = ["15/9-F-5"]
        result = match_well_fuzzy("15/9-F-5", candidates)
        assert result == "15/9-F-5"
    
    def test_normalizes_before_matching(self):
        """Test normalizes well names before matching."""
        candidates = ["15/9-F-5", "15/9-F-4"]
        result = match_well_fuzzy("15_9_F_5", candidates)  # Different format
        assert result is not None
        assert result in candidates
    
    def test_returns_original_well_name(self):
        """Test returns original well name, not normalized."""
        candidates = ["15/9-F-5", "15/9-F-4"]
        result = match_well_fuzzy("15/9-F-5", candidates)
        assert result == "15/9-F-5"  # Original format, not normalized

