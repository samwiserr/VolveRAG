"""
Centralized well name utilities.

This module provides consistent well name normalization and extraction
across the entire codebase, eliminating duplicate implementations.
"""
import re
from typing import Optional
from ..normalize.query_normalizer import extract_well as _extract_well_base, _canonicalize_well


def extract_well(text: str) -> Optional[str]:
    """
    Extract well name from text using centralized logic.
    
    This is a wrapper around the normalize.query_normalizer.extract_well
    to provide a single import point.
    
    Args:
        text: Text to extract well name from
        
    Returns:
        Normalized well name or None
    """
    return _extract_well_base(text)


def normalize_well(well: str) -> str:
    """
    Normalize well name for matching (removes all non-alphanumeric).
    
    This is the standard normalization used across tools for cache lookups.
    Example: "15/9-F-5" -> "159F5"
    
    Args:
        well: Well name to normalize
        
    Returns:
        Normalized well name (uppercase, alphanumeric only)
    """
    return re.sub(r"[^0-9A-Z]+", "", well.upper())


def canonicalize_well(well: str) -> str:
    """
    Canonicalize well name for display and matching.
    
    This preserves the standard format (e.g., "15/9-F-5") while
    normalizing variations. Uses the same logic as query_normalizer.
    
    Args:
        well: Well name to canonicalize
        
    Returns:
        Canonical well name (e.g., "15/9-F-5")
    """
    return _canonicalize_well(well)


def strip_well_suffixes(well: str, suffixes: Optional[list] = None) -> str:
    """
    Strip common suffixes from well names.
    
    Well names in caches may have suffixes like "PETROPHYSICAL", "FORMATION", "REPORT".
    This function removes them for matching purposes.
    
    Args:
        well: Well name (may have suffix)
        suffixes: Optional list of suffixes to strip (defaults to common ones)
        
    Returns:
        Well name with suffixes removed
    """
    if suffixes is None:
        suffixes = ["PETROPHYSICAL", "FORMATION", "REPORT"]
    
    result = well
    for suffix in suffixes:
        if result.endswith(suffix):
            result = result[:-len(suffix)]
            break  # Only strip first matching suffix
    return result


def match_well_fuzzy(query_well: str, candidate_wells: list[str], threshold: float = 0.85) -> Optional[str]:
    """
    Fuzzy match well name against candidates.
    
    Uses rapidfuzz for fuzzy matching with a threshold.
    
    Args:
        query_well: Well name to match
        candidate_wells: List of candidate well names
        threshold: Minimum similarity score (0-1)
        
    Returns:
        Best matching well name or None if below threshold
    """
    try:
        from rapidfuzz import process
        normalized_query = normalize_well(query_well)
        normalized_candidates = [normalize_well(w) for w in candidate_wells]
        
        result = process.extractOne(
            normalized_query,
            normalized_candidates,
            score_cutoff=int(threshold * 100)
        )
        
        if result:
            # Find original well name
            matched_normalized = result[0]
            for orig, norm in zip(candidate_wells, normalized_candidates):
                if norm == matched_normalized:
                    return orig
        return None
    except ImportError:
        # Fallback to exact match if rapidfuzz not available
        normalized_query = normalize_well(query_well)
        for candidate in candidate_wells:
            if normalize_well(candidate) == normalized_query:
                return candidate
        return None

