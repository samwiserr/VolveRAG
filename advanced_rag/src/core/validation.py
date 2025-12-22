"""
Input validation models using Pydantic.

This module provides validated data models for all user inputs,
ensuring type safety and preventing injection attacks.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


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
        
        # Remove null bytes and control characters (except newlines and tabs)
        v = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', v)
        
        # Check for potential injection patterns (basic protection)
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'eval\(',
            r'exec\(',
        ]
        
        query_lower = v.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                raise ValueError(f"Query contains potentially dangerous pattern: {pattern}")
        
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        str_strip_whitespace = True
        validate_assignment = True


class WellNameRequest(BaseModel):
    """
    Validated well name request.
    
    Ensures well names are properly formatted.
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
        """Validate well name format."""
        if not v or not v.strip():
            raise ValueError("Well name cannot be empty")
        
        # Basic format check (should contain numbers)
        if not re.search(r'\d', v):
            raise ValueError("Well name must contain at least one digit")
        
        return v.strip()
    
    class Config:
        str_strip_whitespace = True


class FormationRequest(BaseModel):
    """
    Validated formation name request.
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
        """Validate formation name."""
        if not v or not v.strip():
            raise ValueError("Formation name cannot be empty")
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

