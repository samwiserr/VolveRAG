VolveRAG Documentation
=====================

Welcome to the VolveRAG documentation.

VolveRAG is a LangGraph-based RAG (Retrieval-Augmented Generation) system for querying
petrophysical reports from the Volve dataset.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/core
   api/tools
   api/graph

Core Modules
------------

.. automodule:: src.core
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
------------

The application uses Pydantic Settings for configuration management. All configuration
is loaded from environment variables with sensible defaults.

.. automodule:: src.core.config
   :members:
   :undoc-members:
   :show-inheritance:

Result Pattern
-------------

The application uses a Result monad pattern for explicit error handling.

.. automodule:: src.core.result
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

