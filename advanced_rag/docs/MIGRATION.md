# Migration Guide

## Overview

This guide helps you migrate from the old codebase structure to the new refactored architecture (Phases 0-4).

## Breaking Changes

**None!** All changes maintain backward compatibility. The refactoring is purely additive.

## New Patterns

### 1. Result Pattern for Error Handling

**Old:**
```python
try:
    value = some_operation()
    return value
except Exception as e:
    logger.error(f"Error: {e}")
    return None
```

**New:**
```python
result = some_operation()
if result.is_ok():
    return result.unwrap()
else:
    error = result.error()
    logger.error(f"Error: {error.message}")
    return None
```

### 2. Configuration Management

**Old:**
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
```

**New:**
```python
from src.core.config import get_config
config = get_config()
api_key = config.openai_api_key
model = config.llm_model.value
```

### 3. Well Name Utilities

**Old:**
```python
# Duplicated in multiple files
def normalize_well(s):
    return s.upper().replace("WELL", "").replace("NO", "")
```

**New:**
```python
from src.core.well_utils import normalize_well, extract_well
normalized = normalize_well("15/9-F-5")
```

### 4. Dependency Injection

**Old:**
```python
# Global state
_response_model = None

def get_model():
    global _response_model
    if _response_model is None:
        _response_model = ChatOpenAI(...)
    return _response_model
```

**New:**
```python
from src.core.container import get_container
container = get_container()
model = container.get(ChatOpenAI)
```

### 5. Input Validation

**Old:**
```python
if not query or len(query) > 2000:
    raise ValueError("Invalid query")
```

**New:**
```python
from src.core.validation import validate_query
is_valid, error_msg = validate_query(query)
if not is_valid:
    st.error(f"Invalid query: {error_msg}")
```

## Migration Steps

### Step 1: Update Imports

Replace old imports with new centralized ones:

```python
# Old
from ...core.well_utils import normalize_well  # Relative import

# New
from src.core.well_utils import normalize_well  # Absolute import
```

### Step 2: Replace os.getenv() Calls

```python
# Old
import os
api_key = os.getenv("OPENAI_API_KEY")

# New
from src.core.config import get_config
config = get_config()
api_key = config.openai_api_key
```

### Step 3: Use Result Pattern

Gradually migrate error handling to Result pattern:

```python
# Old
try:
    result = operation()
except Exception as e:
    handle_error(e)

# New
result = operation()
if result.is_err():
    error = result.error()
    handle_error(error)
```

### Step 4: Use Centralized Utilities

Replace duplicate code with centralized utilities:

```python
# Old (duplicated code)
def normalize_well(s):
    # ... implementation ...

# New
from src.core.well_utils import normalize_well
```

### Step 5: Add Input Validation

Add validation to user-facing functions:

```python
# Old
def process_query(query):
    # Process without validation

# New
from src.core.validation import validate_query
def process_query(query):
    is_valid, error = validate_query(query)
    if not is_valid:
        return error
    # Process query
```

## Testing Migration

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -m unit

# Integration tests
pytest tests/integration -m integration

# Property-based tests
pytest tests/property -m property

# Performance tests
pytest tests/performance -m performance
```

### Test Markers

- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.property`: Property-based tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.requires_api`: Needs API keys
- `@pytest.mark.requires_data`: Needs dataset
- `@pytest.mark.requires_vectorstore`: Needs built vectorstore
- `@pytest.mark.slow`: Slow-running tests

## Configuration Migration

### Environment Variables

All environment variables remain the same. New ones:

- `ENABLE_LLM_CACHE`: Enable/disable LLM caching (default: true)
- `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: 3600)
- `MAX_REQUESTS_PER_MINUTE`: Rate limit (default: 60)

### Streamlit Secrets

Add to `.streamlit/secrets.toml`:

```toml
[default]
OPENAI_API_KEY = "your-key-here"
ENABLE_LLM_CACHE = true
CACHE_TTL_SECONDS = 3600
MAX_REQUESTS_PER_MINUTE = 60
```

## Rollback Plan

If you need to rollback:

1. All old code is preserved
2. New code is additive
3. Feature flags allow disabling new features
4. Git history preserves all changes

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review test examples in `tests/`
3. Check phase implementation docs (`PHASE_*.md`)

## Checklist

- [ ] Update imports to use absolute paths
- [ ] Replace `os.getenv()` with `get_config()`
- [ ] Use centralized well utilities
- [ ] Add input validation
- [ ] Migrate error handling to Result pattern
- [ ] Update tests
- [ ] Verify Streamlit compatibility
- [ ] Test in production environment

