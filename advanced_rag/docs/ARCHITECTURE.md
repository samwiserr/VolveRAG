# VolveRAG Architecture Documentation

## Overview

VolveRAG is a state-of-the-art Retrieval-Augmented Generation (RAG) system designed for querying petrophysical reports. The system uses LangGraph for orchestration, OpenAI GPT-4o for generation, and advanced retrieval techniques for accurate answers.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Web UI                        │
│                    (web_app.py)                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                       │
│                  (rag_graph.py)                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Route   │→ │ Retrieve │→ │  Grade   │→ │ Generate │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Routing    │ │  Retrieval   │ │  Generation  │
│  Strategies  │ │    Tools     │ │   Services   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## Core Components

### Phase 0: Foundation

#### Result Monad (`src/core/result.py`)
- Type-safe error handling
- Eliminates bare exception handling
- Explicit error propagation

#### Configuration (`src/core/config.py`)
- Pydantic-based configuration
- Environment variable support
- Streamlit secrets integration
- Type-safe settings

#### Logging (`src/core/logging.py`)
- Structured logging
- Context-aware logging
- JSON format support

### Phase 1: Core Refactoring

#### Routing System (`src/graph/routing/`)
- Strategy pattern for routing
- Deterministic tool selection
- Well/formation/property detection

#### Document Grader (`src/graph/retrieval/document_grader.py`)
- LLM-based relevance scoring
- Context-aware grading
- Caching support

#### Query Rewriter (`src/graph/generation/query_rewriter.py`)
- Query improvement
- Typo correction
- Context enhancement

### Phase 2: Architecture Improvements

#### Dependency Injection (`src/core/container.py`)
- Service container
- Eliminates global state
- Testable architecture

#### Input Validation (`src/core/validation.py`)
- Pydantic models
- Query validation
- Sanitization

#### Utilities (`src/core/well_utils.py`, `src/core/thresholds.py`)
- Centralized well name handling
- Configurable thresholds
- No code duplication

### Phase 3: Performance & Security

#### Caching (`src/core/cache.py`)
- Multi-layer caching
- LLM response caching
- Embedding caching
- TTL support

#### Rate Limiting (`src/core/security.py`)
- Token bucket algorithm
- Per-session tracking
- Configurable limits

#### Security (`src/core/security.py`)
- Input sanitization
- XSS prevention
- Injection protection

## Data Flow

1. **User Query** → Streamlit UI
2. **Validation** → Input validation & sanitization
3. **Rate Limiting** → Check request limits
4. **Query Normalization** → Extract entities (well, formation, property)
5. **Routing** → Determine which tool(s) to use
6. **Retrieval** → Hybrid search (vector + BM25)
7. **Reranking** → Cross-encoder reranking
8. **Grading** → LLM-based relevance check
9. **Generation** → Answer generation with citations
10. **Response** → Return to user

## Tools

### RetrieverTool
- Hybrid search (vector + BM25)
- Cross-encoder reranking
- LLM reranking
- MMR diversification

### PetroParamsTool
- Structured parameter lookup
- Fuzzy formation matching
- Well name normalization
- Cached results

### WellPicksTool
- Well picks lookup
- Depth-based queries
- Formation boundaries

### EvalParamsTool
- Evaluation parameters
- Matrix/fluid properties
- Archie parameters

### SectionLookupTool
- Document section lookup
- Table extraction
- Structured data access

## Configuration

All configuration is managed through `AppConfig` in `src/core/config.py`:

- **API Keys**: OpenAI API key
- **Models**: LLM, embedding, grading models
- **Paths**: Vectorstore, documents
- **Retrieval**: Chunk size, overlap, MMR lambda
- **Thresholds**: Fuzzy matching, formation matching
- **Features**: Query decomposition, completion, entity resolution
- **Caching**: Enable/disable, TTL
- **Rate Limiting**: Requests per minute

## Error Handling

The system uses the Result monad pattern for type-safe error handling:

```python
result = some_operation()
if result.is_ok():
    value = result.unwrap()
else:
    error = result.error()
    # Handle error
```

Error types:
- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND_ERROR`: Resource not found
- `RATE_LIMIT_ERROR`: Rate limit exceeded
- `LLM_ERROR`: LLM API error
- `PROCESSING_ERROR`: General processing error

## Testing

### Unit Tests (`tests/unit/`)
- Core utilities
- Result monad
- Configuration
- Path resolution

### Integration Tests (`tests/integration/`)
- Full RAG workflow
- Tool orchestration
- Error propagation
- End-to-end scenarios

### Property-Based Tests (`tests/property/`)
- Well normalization properties
- Query expansion properties
- Edge case discovery

### Performance Tests (`tests/performance/`)
- Cache performance
- Response times
- Throughput

## Deployment

### Streamlit Cloud
- Automatic deployment from GitHub
- Environment variables via secrets
- Asset downloads from GitHub Releases
- Session-based rate limiting

### Local Development
```bash
streamlit run web_app.py
```

## Best Practices

1. **Always use Result pattern** for error handling
2. **Use DI container** instead of global state
3. **Validate all inputs** with Pydantic
4. **Use centralized utilities** (well_utils, thresholds)
5. **Cache expensive operations** (LLM calls, embeddings)
6. **Log with context** for debugging
7. **Test thoroughly** with unit, integration, and property tests

## Future Enhancements

- Redis cache for multi-instance deployments
- Async I/O for better concurrency
- Advanced monitoring and metrics
- A/B testing framework
- Multi-modal support (images, tables)

