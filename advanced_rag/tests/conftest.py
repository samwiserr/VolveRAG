"""
Pytest configuration and shared fixtures.
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_vectorstore(tmp_path):
    """
    Create temporary vectorstore directory.
    
    Yields:
        Path to temporary vectorstore directory
    """
    vs_dir = tmp_path / "vectorstore"
    vs_dir.mkdir(parents=True)
    yield vs_dir
    shutil.rmtree(vs_dir, ignore_errors=True)


@pytest.fixture
def temp_documents(tmp_path):
    """
    Create temporary documents directory.
    
    Yields:
        Path to temporary documents directory
    """
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir(parents=True)
    yield docs_dir
    shutil.rmtree(docs_dir, ignore_errors=True)


@pytest.fixture
def mock_openai_client(monkeypatch):
    """
    Mock OpenAI client for testing.
    
    Returns:
        Mock OpenAI client
    """
    mock_client = MagicMock()
    
    # Mock ChatOpenAI
    def mock_chat_openai(*args, **kwargs):
        return mock_client
    
    monkeypatch.setattr("langchain_openai.ChatOpenAI", mock_chat_openai)
    
    # Mock OpenAIEmbeddings
    def mock_embeddings(*args, **kwargs):
        mock_emb = MagicMock()
        mock_emb.embed_query.return_value = [0.1] * 1536  # Mock embedding
        return mock_emb
    
    monkeypatch.setattr("langchain_openai.OpenAIEmbeddings", mock_embeddings)
    
    return mock_client


@pytest.fixture
def sample_well_names():
    """
    Sample well names for testing.
    
    Returns:
        List of well name strings
    """
    return [
        "15/9-F-5",
        "15/9-F-4",
        "15/9-19A",
        "15/9-F-15A",
        "15/9-F-1",
    ]


@pytest.fixture
def sample_documents():
    """
    Sample document chunks for testing.
    
    Returns:
        List of document dictionaries
    """
    return [
        {
            "page_content": "Hugin formation has porosity of 0.25 and water saturation of 0.30.",
            "metadata": {"source": "test.pdf", "page": 1, "filename": "test.pdf"}
        },
        {
            "page_content": "Sleipner formation depth ranges from 2500m to 2800m.",
            "metadata": {"source": "test.pdf", "page": 2, "filename": "test.pdf"}
        },
        {
            "page_content": "Well 15/9-F-5 was drilled in 2014.",
            "metadata": {"source": "test.pdf", "page": 3, "filename": "test.pdf"}
        },
    ]


@pytest.fixture
def mock_config(monkeypatch):
    """
    Mock configuration for testing.
    
    Returns:
        Mock config object
    """
    from src.core.config import AppConfig, EmbeddingModel, LLMModel, LogLevel
    
    mock_config = MagicMock(spec=AppConfig)
    mock_config.openai_api_key = "test-api-key"
    mock_config.embedding_model = EmbeddingModel.TEXT_EMBEDDING_3_SMALL
    mock_config.llm_model = LLMModel.GPT_4O
    mock_config.grade_model = LLMModel.GPT_4O
    mock_config.persist_directory = Path("./data/vectorstore")
    mock_config.documents_path = None
    mock_config.chunk_size = 500
    mock_config.chunk_overlap = 150
    mock_config.use_cross_encoder = True
    mock_config.mmr_enabled = True
    mock_config.mmr_lambda = 0.7
    mock_config.formation_fuzzy_threshold = 85.0
    mock_config.formation_fuzzy_margin = 10.0
    mock_config.enable_query_decomposition = True
    mock_config.enable_query_completion = True
    mock_config.log_level = LogLevel.INFO
    mock_config.log_format = "text"
    mock_config.max_requests_per_minute = 60
    mock_config.enable_llm_cache = True
    mock_config.cache_ttl_seconds = 3600
    
    # Patch get_config to return mock
    def mock_get_config():
        return mock_config
    
    monkeypatch.setattr("src.core.config.get_config", mock_get_config)
    
    return mock_config


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    """
    Reset config singleton before each test.
    
    This ensures tests don't interfere with each other.
    """
    from src.core.config import reload_config
    reload_config()
    yield
    reload_config()

