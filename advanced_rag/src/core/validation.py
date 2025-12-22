"""
Input validation models using Pydantic.

This module provides validated data models for all user inputs,
ensuring type safety and preventing injection attacks.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


# Request size limits (in bytes)
MAX_QUERY_SIZE_BYTES: int = 10000  # ~10KB max query size
MAX_WELL_SIZE_BYTES: int = 200  # ~200 bytes max well name size
MAX_FORMATION_SIZE_BYTES: int = 500  # ~500 bytes max formation name size


class QueryRequest(BaseModel):
    """
    Validated query request model.
    
    Ensures queries are safe, properly formatted, and within limits.
    """
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User query string"
    )
    
    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """
        Validate and sanitize query string.
        
        Args:
            v: Query string
            
        Returns:
            Sanitized query string
            
        Raises:
            ValueError: If query is invalid or contains dangerous patterns
        """
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Check request size (in bytes)
        query_bytes = len(v.encode('utf-8'))
        if query_bytes > MAX_QUERY_SIZE_BYTES:
            raise ValueError(f"Query too large: {query_bytes} bytes (max {MAX_QUERY_SIZE_BYTES} bytes)")
        
        # Remove null bytes and control characters (except newlines and tabs)
        v = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', v)
        
        # Check for potential injection patterns (enhanced protection)
        dangerous_patterns = [
            (r'<script', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'onerror=', 'Event handlers'),
            (r'onload=', 'Event handlers'),
            (r'eval\(', 'Eval function'),
            (r'exec\(', 'Exec function'),
            (r'import\s+os', 'OS import'),
            (r'__import__', 'Dynamic import'),
            (r'subprocess', 'Subprocess execution'),
            (r'shell\s*=', 'Shell assignment'),
        ]
        
        query_lower = v.lower()
        for pattern, description in dangerous_patterns:
            if re.search(pattern, query_lower):
                raise ValueError(f"Query contains potentially dangerous pattern: {description}")
        
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True
        validate_assignment = True


class WellNameRequest(BaseModel):
    """
    Validated well name request.
    
    Ensures well names are properly formatted and safe.
    """
    well: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Well name (e.g., 15/9-F-5)"
    )
    
    @field_validator("well")
    @classmethod
    def validate_well(cls, v: str) -> str:
        """Validate well name format and safety."""
        if not v or not v.strip():
            raise ValueError("Well name cannot be empty")
        
        # Check request size (in bytes)
        well_bytes = len(v.encode('utf-8'))
        if well_bytes > MAX_WELL_SIZE_BYTES:
            raise ValueError(f"Well name too large: {well_bytes} bytes (max {MAX_WELL_SIZE_BYTES} bytes)")
        
        # Remove null bytes and control characters
        v = re.sub(r'[\x00-\x1f]', '', v)
        
        # Basic format check (should contain numbers)
        if not re.search(r'\d', v):
            raise ValueError("Well name must contain at least one digit")
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'<script', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'\.\./', 'Path traversal'),
            (r'\.\.\\', 'Path traversal'),
        ]
        
        well_lower = v.lower()
        for pattern, description in dangerous_patterns:
            if re.search(pattern, well_lower):
                raise ValueError(f"Well name contains potentially dangerous pattern: {description}")
        
        return v.strip()
    
    class Config:
        str_strip_whitespace = True


class FormationRequest(BaseModel):
    """
    Validated formation name request.
    
    Ensures formation names are safe and properly formatted.
    """
    formation: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Formation name (e.g., Hugin, Sleipner)"
    )
    
    @field_validator("formation")
    @classmethod
    def validate_formation(cls, v: str) -> str:
        """Validate formation name format and safety."""
        if not v or not v.strip():
            raise ValueError("Formation name cannot be empty")
        
        # Check request size (in bytes)
        formation_bytes = len(v.encode('utf-8'))
        if formation_bytes > MAX_FORMATION_SIZE_BYTES:
            raise ValueError(f"Formation name too large: {formation_bytes} bytes (max {MAX_FORMATION_SIZE_BYTES} bytes)")
        
        # Remove null bytes and control characters
        v = re.sub(r'[\x00-\x1f]', '', v)
        
        # Check for dangerous patterns
        dangerous_patterns = [
            (r'<script', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'\.\./', 'Path traversal'),
            (r'\.\.\\', 'Path traversal'),
        ]
        
        formation_lower = v.lower()
        for pattern, description in dangerous_patterns:
            if re.search(pattern, formation_lower):
                raise ValueError(f"Formation name contains potentially dangerous pattern: {description}")
        
        return v.strip()
    
    class Config:
        str_strip_whitespace = True


def validate_query(query: str) -> tuple[bool, Optional[str]]:
    """
    Validate query string (convenience function).
    
    Args:
        query: Query string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        QueryRequest(query=query)
        return True, None
    except Exception as e:
        return False, str(e)

