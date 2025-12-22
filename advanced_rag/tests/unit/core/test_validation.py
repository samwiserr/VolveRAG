"""
Unit tests for validation module.
"""
import pytest
from pydantic import ValidationError
from src.core.validation import (
    QueryRequest,
    WellNameRequest,
    FormationRequest,
    validate_query
)


@pytest.mark.unit
class TestQueryRequest:
    """Test QueryRequest model."""
    
    def test_validates_valid_query(self):
        """Test validates valid query."""
        request = QueryRequest(query="What is the porosity of well 15/9-F-5?")
        assert request.query == "What is the porosity of well 15/9-F-5?"
    
    def test_strips_whitespace(self):
        """Test strips whitespace from query."""
        request = QueryRequest(query="  query with spaces  ")
        assert request.query == "query with spaces"
    
    def test_rejects_empty_query(self):
        """Test rejects empty query."""
        with pytest.raises(ValidationError):
            QueryRequest(query="")
    
    def test_rejects_whitespace_only_query(self):
        """Test rejects whitespace-only query."""
        with pytest.raises(ValidationError):
            QueryRequest(query="   ")
    
    def test_enforces_min_length(self):
        """Test enforces minimum length."""
        request = QueryRequest(query="a")
        assert request.query == "a"
    
    def test_enforces_max_length(self):
        """Test enforces maximum length."""
        long_query = "a" * 2000
        request = QueryRequest(query=long_query)
        assert len(request.query) == 2000
        
        with pytest.raises(ValidationError):
            QueryRequest(query="a" * 2001)
    
    def test_removes_null_bytes(self):
        """Test removes null bytes."""
        request = QueryRequest(query="query\x00with\x00nulls")
        assert "\x00" not in request.query
    
    def test_removes_control_characters(self):
        """Test removes control characters."""
        request = QueryRequest(query="query\x01\x02\x03text")
        assert "\x01" not in request.query
        assert "\x02" not in request.query
        assert "\x03" not in request.query
    
    def test_preserves_newlines_and_tabs(self):
        """Test preserves newlines and tabs."""
        request = QueryRequest(query="query\nwith\ttabs")
        assert "\n" in request.query
        assert "\t" in request.query
    
    def test_rejects_script_tags(self):
        """Test rejects script tags."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query <script>alert('xss')</script>")
    
    def test_rejects_javascript_protocol(self):
        """Test rejects javascript: protocol."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query javascript:alert('xss')")
    
    def test_rejects_onerror_attributes(self):
        """Test rejects onerror attributes."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query onerror=alert('xss')")
    
    def test_rejects_onload_attributes(self):
        """Test rejects onload attributes."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query onload=alert('xss')")
    
    def test_rejects_eval_calls(self):
        """Test rejects eval() calls."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query eval('malicious')")
    
    def test_rejects_exec_calls(self):
        """Test rejects exec() calls."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query exec('malicious')")
    
    def test_case_insensitive_dangerous_patterns(self):
        """Test dangerous pattern detection is case-insensitive."""
        with pytest.raises(ValidationError):
            QueryRequest(query="query <SCRIPT>alert('xss')</SCRIPT>")
        
        with pytest.raises(ValidationError):
            QueryRequest(query="query JAVASCRIPT:alert('xss')")


@pytest.mark.unit
class TestWellNameRequest:
    """Test WellNameRequest model."""
    
    def test_validates_valid_well_name(self):
        """Test validates valid well name."""
        request = WellNameRequest(well="15/9-F-5")
        assert request.well == "15/9-F-5"
    
    def test_strips_whitespace(self):
        """Test strips whitespace."""
        request = WellNameRequest(well="  15/9-F-5  ")
        assert request.well == "15/9-F-5"
    
    def test_rejects_empty_well_name(self):
        """Test rejects empty well name."""
        with pytest.raises(ValidationError):
            WellNameRequest(well="")
    
    def test_rejects_whitespace_only_well_name(self):
        """Test rejects whitespace-only well name."""
        with pytest.raises(ValidationError):
            WellNameRequest(well="   ")
    
    def test_enforces_min_length(self):
        """Test enforces minimum length."""
        request = WellNameRequest(well="1")
        assert request.well == "1"
    
    def test_enforces_max_length(self):
        """Test enforces maximum length."""
        # Use well name with digits (required by validation)
        # "15/9-F-5" = 8 chars, need 42 more to reach 50
        long_well = "15/9-F-5" + "5" * 42  # Total 50 chars
        request = WellNameRequest(well=long_well)
        assert len(request.well) == 50
        
        with pytest.raises(ValidationError):
            WellNameRequest(well="15/9-F-5" + "5" * 43)  # Total 51 chars
    
    def test_requires_at_least_one_digit(self):
        """Test requires at least one digit."""
        with pytest.raises(ValidationError):
            WellNameRequest(well="ABC")
        
        # Should accept well with digits
        request = WellNameRequest(well="15/9-F-5")
        assert request.well == "15/9-F-5"


@pytest.mark.unit
class TestFormationRequest:
    """Test FormationRequest model."""
    
    def test_validates_valid_formation_name(self):
        """Test validates valid formation name."""
        request = FormationRequest(formation="Hugin")
        assert request.formation == "Hugin"
    
    def test_strips_whitespace(self):
        """Test strips whitespace."""
        request = FormationRequest(formation="  Hugin  ")
        assert request.formation == "Hugin"
    
    def test_rejects_empty_formation_name(self):
        """Test rejects empty formation name."""
        with pytest.raises(ValidationError):
            FormationRequest(formation="")
    
    def test_rejects_whitespace_only_formation_name(self):
        """Test rejects whitespace-only formation name."""
        with pytest.raises(ValidationError):
            FormationRequest(formation="   ")
    
    def test_enforces_min_length(self):
        """Test enforces minimum length."""
        request = FormationRequest(formation="A")
        assert request.formation == "A"
    
    def test_enforces_max_length(self):
        """Test enforces maximum length."""
        long_formation = "a" * 100
        request = FormationRequest(formation=long_formation)
        assert len(request.formation) == 100
        
        with pytest.raises(ValidationError):
            FormationRequest(formation="a" * 101)


@pytest.mark.unit
class TestValidateQuery:
    """Test validate_query convenience function."""
    
    def test_returns_true_for_valid_query(self):
        """Test returns True for valid query."""
        is_valid, error = validate_query("What is the porosity?")
        assert is_valid is True
        assert error is None
    
    def test_returns_false_for_invalid_query(self):
        """Test returns False for invalid query."""
        is_valid, error = validate_query("")
        assert is_valid is False
        assert error is not None
        assert isinstance(error, str)
        assert len(error) > 0
    
    def test_returns_false_for_dangerous_query(self):
        """Test returns False for dangerous query."""
        is_valid, error = validate_query("<script>alert('xss')</script>")
        assert is_valid is False
        assert error is not None
    
    def test_returns_error_message_for_empty_query(self):
        """Test returns error message for empty query."""
        is_valid, error = validate_query("")
        assert is_valid is False
        assert isinstance(error, str)
        assert len(error) > 0
    
    def test_handles_whitespace_only_query(self):
        """Test handles whitespace-only query."""
        is_valid, error = validate_query("   ")
        assert is_valid is False
        assert error is not None

