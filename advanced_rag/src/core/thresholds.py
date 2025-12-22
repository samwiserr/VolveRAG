"""
Centralized thresholds and magic numbers.

This module provides a single source of truth for all numeric thresholds,
replacing hardcoded values throughout the codebase.
"""
from dataclasses import dataclass
from typing import Optional
from .config import get_config


@dataclass
class MatchingThresholds:
    """Thresholds for fuzzy matching and entity resolution."""
    formation_fuzzy_threshold: float = 85.0
    formation_fuzzy_margin: float = 10.0
    well_fuzzy_threshold: float = 85.0
    
    @classmethod
    def from_config(cls) -> "MatchingThresholds":
        """Load thresholds from configuration."""
        try:
            config = get_config()
            return cls(
                formation_fuzzy_threshold=config.formation_fuzzy_threshold,
                formation_fuzzy_margin=config.formation_fuzzy_margin,
            )
        except Exception:
            # Fallback to defaults if config not available
            return cls()


@dataclass
class RetrievalThresholds:
    """Thresholds for document retrieval."""
    chunk_size: int = 500
    chunk_overlap: int = 150
    mmr_lambda: float = 0.7
    max_query_length: int = 5000
    min_context_length: int = 50
    max_context_length: int = 3000
    
    @classmethod
    def from_config(cls) -> "RetrievalThresholds":
        """Load thresholds from configuration."""
        try:
            config = get_config()
            return cls(
                chunk_size=config.chunk_size,
                chunk_overlap=config.chunk_overlap,
                mmr_lambda=config.mmr_lambda,
            )
        except Exception:
            # Fallback to defaults if config not available
            return cls()


def get_matching_thresholds() -> MatchingThresholds:
    """Get matching thresholds (singleton)."""
    return MatchingThresholds.from_config()


def get_retrieval_thresholds() -> RetrievalThresholds:
    """Get retrieval thresholds (singleton)."""
    return RetrievalThresholds.from_config()

