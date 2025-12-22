"""
Citation parsing logic for extracting source references from answers.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

__all__ = ["Citation", "_parse_citations", "_clean_source_path", "_normalize_source_path"]


@dataclass
class Citation:
    """Represents a citation with source path and page range."""
    source_path: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None


def _clean_source_path(source_path: str) -> str:
    """
    Clean up source path to show a user-friendly filename or relative path.
    Removes local Windows paths and shows just the filename or well/filename.
    
    Args:
        source_path: Original source path (may be full Windows path)
        
    Returns:
        Cleaned path (e.g., "15_9-F-5/PETROPHYSICAL_REPORT_1.PDF" or just filename)
    """
    if not source_path:
        return source_path
    
    # Handle Windows paths and relative paths
    path_str = source_path.replace('\\', '/')
    parts = [p for p in path_str.split('/') if p and p != '..' and p != '.']
    
    # Remove common prefixes like "C:", "Users", "Downloads", "spwla_volve-main"
    filtered_parts = []
    skip_next = False
    for i, part in enumerate(parts):
        if skip_next:
            skip_next = False
            continue
        # Skip drive letters, common user dirs
        if part.endswith(':') or part.lower() in ['users', 'downloads', 'spwla_volve-main']:
            continue
        # Keep well directories and filenames
        if re.match(r'^\d+[\s_/-]*\d+', part) or part.lower().endswith('.pdf'):
            filtered_parts.append(part)
    
    # If we have well directory and filename, return "well_dir/filename"
    if len(filtered_parts) >= 2:
        return '/'.join(filtered_parts[-2:])
    # Otherwise just return the filename
    elif filtered_parts:
        return filtered_parts[-1]
    else:
        # Fallback: just get the filename from the original path
        return Path(source_path).name


def _normalize_source_path(source_path: str) -> str:
    """
    Normalize source path for consistent handling.
    Converts backslashes to forward slashes and handles relative paths.
    
    Args:
        source_path: Source path (may have backslashes, relative paths)
        
    Returns:
        Normalized path string
    """
    if not source_path:
        return source_path
    
    # Convert backslashes to forward slashes for consistency
    normalized = source_path.replace('\\', '/')
    
    # Handle relative paths (remove leading .. or .)
    parts = [p for p in normalized.split('/') if p and p != '.']
    # Remove leading '..' parts but keep the rest
    while parts and parts[0] == '..':
        parts.pop(0)
    
    return '/'.join(parts) if parts else normalized


def _parse_citations(answer: str) -> List[Citation]:
    """
    Extract citations from tool outputs like:
      Source: C:\\path\\file.pdf (pages 12-13)
      Source: C:\\path\\file.pdf (page 12)
      Source: ..\\spwla_volve-main\\15_9-F-5\\PETROPHYSICAL_REPORT_1.PDF (pages 3-4)
    
    Handles both Windows and Unix path formats, relative paths, and various whitespace.
    """
    if not isinstance(answer, str) or not answer.strip():
        return []

    cits: List[Citation] = []
    seen = set()  # Avoid duplicates

    # Normalize line endings and split into lines for more robust parsing
    lines = answer.split('\n')
    
    # Pattern 1: Source: path (pages X-Y) - most common format
    # Match on individual lines for better reliability
    for line in lines:
        line = line.strip()
        if not line.startswith('Source:'):
            continue
            
        # Pattern 1a: Source: path (pages X-Y)
        match = re.match(
            r"^Source:\s*(.+?)\s*\(pages\s+(\d+)\s*-\s*(\d+)\)\s*$",
            line,
        )
        if match:
            source = _normalize_source_path(match.group(1).strip())
            page_start = int(match.group(2))
            page_end = int(match.group(3))
            key = (source, page_start, page_end)
            if key not in seen:
                seen.add(key)
                cits.append(Citation(source, page_start, page_end))
                continue
        
        # Pattern 1b: Source: path (page X)
        match = re.match(
            r"^Source:\s*(.+?)\s*\(page\s+(\d+)\)\s*$",
            line,
        )
        if match:
            source = _normalize_source_path(match.group(1).strip())
            page = int(match.group(2))
            key = (source, page, page)
            if key not in seen:
                seen.add(key)
                cits.append(Citation(source, page, page))
                continue
        
        # Pattern 1c: Source: path (no page info) - fallback
        match = re.match(r"^Source:\s*(.+?)\s*$", line)
        if match:
            source = _normalize_source_path(match.group(1).strip())
            # Skip if it looks like it has page info but didn't match (avoid duplicates)
            if "(page" not in source and "(pages" not in source and source != "N/A":
                if source not in seen:
                    seen.add(source)
                    cits.append(Citation(source))
    
    # Also try multiline regex as fallback (for edge cases)
    if not cits:
        # Pattern 2: Source: path (pages X-Y) - multiline regex
        for m in re.finditer(
            r"^Source:\s*(.+?)\s*\(pages\s+(\d+)\s*-\s*(\d+)\)\s*$",
            answer,
            flags=re.MULTILINE,
        ):
            source = _normalize_source_path(m.group(1).strip())
            page_start = int(m.group(2))
            page_end = int(m.group(3))
            key = (source, page_start, page_end)
            if key not in seen:
                seen.add(key)
                cits.append(Citation(source, page_start, page_end))

        # Pattern 3: Source: path (page X) - multiline regex
        for m in re.finditer(
            r"^Source:\s*(.+?)\s*\(page\s+(\d+)\)\s*$",
            answer,
            flags=re.MULTILINE,
        ):
            source = _normalize_source_path(m.group(1).strip())
            page = int(m.group(2))
            key = (source, page, page)
            if key not in seen:
                seen.add(key)
                cits.append(Citation(source, page, page))

    return cits

