"""
Unit tests for thresholds module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.core.thresholds import (
    MatchingThresholds,
    RetrievalThresholds,
    get_matching_thresholds,
    get_retrieval_thresholds
)


@pytest.mark.unit
class TestMatchingThresholds:
    """Test MatchingThresholds dataclass."""
    
    def test_default_values(self):
        """Test default threshold values."""
        thresholds = MatchingThresholds()
        assert thresholds.formation_fuzzy_threshold == 85.0
        assert thresholds.formation_fuzzy_margin == 10.0
        assert thresholds.well_fuzzy_threshold == 85.0
    
    def test_custom_values(self):
        """Test custom threshold values."""
        thresholds = MatchingThresholds(
            formation_fuzzy_threshold=90.0,
            formation_fuzzy_margin=15.0,
            well_fuzzy_threshold=80.0
        )
        assert thresholds.formation_fuzzy_threshold == 90.0
        assert thresholds.formation_fuzzy_margin == 15.0
        assert thresholds.well_fuzzy_threshold == 80.0
    
    @patch('src.core.thresholds.get_config')
    def test_from_config_loads_values(self, mock_get_config):
        """Test from_config loads values from config."""
        mock_config = MagicMock()
        mock_config.formation_fuzzy_threshold = 90.0
        mock_config.formation_fuzzy_margin = 15.0
        mock_get_config.return_value = mock_config
        
        thresholds = MatchingThresholds.from_config()
        assert thresholds.formation_fuzzy_threshold == 90.0
        assert thresholds.formation_fuzzy_margin == 15.0
        # well_fuzzy_threshold should use default if not in config
        assert thresholds.well_fuzzy_threshold == 85.0
    
    @patch('src.core.thresholds.get_config')
    def test_from_config_fallback_on_error(self, mock_get_config):
        """Test from_config falls back to defaults on error."""
        mock_get_config.side_effect = Exception("Config error")
        
        thresholds = MatchingThresholds.from_config()
        # Should use defaults
        assert thresholds.formation_fuzzy_threshold == 85.0
        assert thresholds.formation_fuzzy_margin == 10.0
        assert thresholds.well_fuzzy_threshold == 85.0


@pytest.mark.unit
class TestRetrievalThresholds:
    """Test RetrievalThresholds dataclass."""
    
    def test_default_values(self):
        """Test default threshold values."""
        thresholds = RetrievalThresholds()
        assert thresholds.chunk_size == 500
        assert thresholds.chunk_overlap == 150
        assert thresholds.mmr_lambda == 0.7
        assert thresholds.max_query_length == 5000
        assert thresholds.min_context_length == 50
        assert thresholds.max_context_length == 3000
    
    def test_custom_values(self):
        """Test custom threshold values."""
        thresholds = RetrievalThresholds(
            chunk_size=1000,
            chunk_overlap=200,
            mmr_lambda=0.8,
            max_query_length=10000,
            min_context_length=100,
            max_context_length=5000
        )
        assert thresholds.chunk_size == 1000
        assert thresholds.chunk_overlap == 200
        assert thresholds.mmr_lambda == 0.8
        assert thresholds.max_query_length == 10000
        assert thresholds.min_context_length == 100
        assert thresholds.max_context_length == 5000
    
    @patch('src.core.thresholds.get_config')
    def test_from_config_loads_values(self, mock_get_config):
        """Test from_config loads values from config."""
        mock_config = MagicMock()
        mock_config.chunk_size = 1000
        mock_config.chunk_overlap = 200
        mock_config.mmr_lambda = 0.8
        mock_get_config.return_value = mock_config
        
        thresholds = RetrievalThresholds.from_config()
        assert thresholds.chunk_size == 1000
        assert thresholds.chunk_overlap == 200
        assert thresholds.mmr_lambda == 0.8
        # Other values should use defaults
        assert thresholds.max_query_length == 5000
    
    @patch('src.core.thresholds.get_config')
    def test_from_config_fallback_on_error(self, mock_get_config):
        """Test from_config falls back to defaults on error."""
        mock_get_config.side_effect = Exception("Config error")
        
        thresholds = RetrievalThresholds.from_config()
        # Should use defaults
        assert thresholds.chunk_size == 500
        assert thresholds.chunk_overlap == 150
        assert thresholds.mmr_lambda == 0.7


@pytest.mark.unit
class TestGetThresholds:
    """Test get_*_thresholds convenience functions."""
    
    @patch('src.core.thresholds.MatchingThresholds.from_config')
    def test_get_matching_thresholds(self, mock_from_config):
        """Test get_matching_thresholds function."""
        mock_thresholds = MatchingThresholds()
        mock_from_config.return_value = mock_thresholds
        
        result = get_matching_thresholds()
        assert result == mock_thresholds
        mock_from_config.assert_called_once()
    
    @patch('src.core.thresholds.RetrievalThresholds.from_config')
    def test_get_retrieval_thresholds(self, mock_from_config):
        """Test get_retrieval_thresholds function."""
        mock_thresholds = RetrievalThresholds()
        mock_from_config.return_value = mock_thresholds
        
        result = get_retrieval_thresholds()
        assert result == mock_thresholds
        mock_from_config.assert_called_once()

