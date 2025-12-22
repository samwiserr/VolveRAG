"""
Streamlit Web UI for the LangGraph-based Petrophysical RAG system.

This file is maintained for backward compatibility. The actual implementation has been
split into modular components in the web_app/ directory.

To run the app:
    streamlit run web_app.py
    OR
    streamlit run web_app/app.py
"""

from __future__ import annotations

# Import main function and all public functions from new modular structure
from web_app.app import main
from web_app.logic.citation_parser import Citation, _parse_citations, _clean_source_path
from web_app.logic.asset_downloader import (
    _download_and_extract_pdfs,
    _download_and_extract_vectorstore,
    _ensure_pdfs_available,
    _ensure_vectorstore_available
)
from web_app.logic.pdf_viewer import (
    _find_pdf_file,
    _pdf_full_viewer,
    _get_pdf_data_uri,
    _pdf_iframe,
    _render_pdf_page_png
)
from web_app.logic.graph_manager import _get_graph

# Re-export for backward compatibility
__all__ = [
    "main",
    "Citation",
    "_parse_citations",
    "_clean_source_path",
    "_download_and_extract_pdfs",
    "_download_and_extract_vectorstore",
    "_ensure_pdfs_available",
    "_ensure_vectorstore_available",
    "_find_pdf_file",
    "_pdf_full_viewer",
    "_get_pdf_data_uri",
    "_pdf_iframe",
    "_render_pdf_page_png",
    "_get_graph",
]

# Streamlit executes files directly, so call main() at module level
# This ensures the app runs when Streamlit executes this file via `streamlit run web_app.py`
# Note: This file is meant to be executed by Streamlit, not imported as a module
try:
    main()
except Exception as e:
    # If main() fails, try to show error in Streamlit
    try:
        import streamlit as st
        st.error(f"Application failed to start: {e}")
        st.exception(e)
    except:
        # If Streamlit isn't available, just raise the error
        import traceback
        traceback.print_exc()
        raise
