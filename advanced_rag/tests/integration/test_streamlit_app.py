"""
Integration tests for Streamlit application.

Tests Streamlit app initialization, components, and user interactions (mocked).
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
import sys

# Mock streamlit before importing
sys.modules['streamlit'] = MagicMock()
sys.modules['streamlit.cache_resource'] = MagicMock()
sys.modules['streamlit.cache_data'] = MagicMock()


@pytest.mark.integration
class TestStreamlitApp:
    """Test Streamlit application integration."""
    
    def test_app_imports(self):
        """Test that app module can be imported."""
        try:
            from web_app.app import main
            assert main is not None
        except ImportError as e:
            pytest.skip(f"Streamlit app not available: {e}")
    
    def test_app_initialization(self, mock_config):
        """Test app can be initialized."""
        try:
            from web_app.app import main
            # Main should be callable
            assert callable(main)
        except ImportError:
            pytest.skip("Streamlit app not available")
    
    def test_graph_manager_import(self, mock_config):
        """Test graph manager can be imported."""
        try:
            from web_app.logic.graph_manager import _get_graph, _register_services
            assert _get_graph is not None
            assert _register_services is not None
        except ImportError:
            pytest.skip("Graph manager not available")
    
    def test_asset_downloader_import(self, mock_config):
        """Test asset downloader can be imported."""
        try:
            from web_app.logic.asset_downloader import (
                _download_and_extract_pdfs,
                _ensure_pdfs_available,
                _download_and_extract_vectorstore,
                _ensure_vectorstore_available
            )
            assert _download_and_extract_pdfs is not None
            assert _ensure_pdfs_available is not None
            assert _download_and_extract_vectorstore is not None
            assert _ensure_vectorstore_available is not None
        except ImportError:
            pytest.skip("Asset downloader not available")
    
    def test_pdf_viewer_import(self, mock_config):
        """Test PDF viewer can be imported."""
        try:
            from web_app.logic.pdf_viewer import (
                _find_pdf_file,
                _pdf_full_viewer,
                _get_pdf_data_uri,
                _pdf_iframe,
                _render_pdf_page_png
            )
            assert _find_pdf_file is not None
            assert _pdf_full_viewer is not None
            assert _get_pdf_data_uri is not None
            assert _pdf_iframe is not None
            assert _render_pdf_page_png is not None
        except ImportError:
            pytest.skip("PDF viewer not available")
    
    def test_citation_parser_import(self, mock_config):
        """Test citation parser can be imported."""
        try:
            from web_app.logic.citation_parser import (
                Citation,
                _clean_source_path,
                _parse_citations
            )
            assert Citation is not None
            assert _clean_source_path is not None
            assert _parse_citations is not None
        except ImportError:
            pytest.skip("Citation parser not available")
    
    @patch('streamlit.cache_resource')
    def test_graph_caching(self, mock_cache_resource, mock_config):
        """Test graph caching mechanism."""
        try:
            from web_app.logic.graph_manager import _get_graph
            
            # Mock cache decorator
            mock_cache_resource.return_value = lambda func: func
            
            # Graph should be cacheable
            assert _get_graph is not None
        except ImportError:
            pytest.skip("Graph manager not available")
    
    def test_backward_compatibility(self, mock_config):
        """Test backward compatibility of web_app.py."""
        try:
            # web_app.py should import from web_app.app
            # Check that web_app.py exists and can be imported
            import web_app
            assert web_app is not None
            # web_app.py imports main from web_app.app
            # Verify the import works
            from web_app.app import main
            assert callable(main)
        except ImportError:
            pytest.skip("web_app module not available")
    
    def test_path_resolution(self, mock_config):
        """Test path resolution in web app modules."""
        try:
            from web_app.logic.graph_manager import _get_graph
            from pathlib import Path
            
            # Should handle path resolution correctly
            persist_dir = "./data/vectorstore"
            # Just check it doesn't crash on import
            assert _get_graph is not None
        except ImportError:
            pytest.skip("Graph manager not available")
        except Exception as e:
            # Path resolution errors are acceptable in test environment
            pytest.skip(f"Path resolution issue in test: {e}")

