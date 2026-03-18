"""Ingestion framework - fetchers and data pipeline.

Importing this module auto-registers all fetchers via their module-level
``registry.register()`` calls.
"""

from app.ingestion import arxiv as _arxiv  # noqa: F401
from app.ingestion import github_trending as _github  # noqa: F401
from app.ingestion import huggingface as _hf  # noqa: F401
