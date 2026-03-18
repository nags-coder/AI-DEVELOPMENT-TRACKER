"""Fetcher registry - maps source names to fetcher classes."""

from app.ingestion.base import BaseFetcher


class FetcherRegistry:
    """Registry that maps source names to fetcher instances.

    Usage:
        registry = FetcherRegistry()
        registry.register(ArxivFetcher())
        fetcher = registry.get("arXiv")
    """

    def __init__(self) -> None:
        self._fetchers: dict[str, BaseFetcher] = {}

    def register(self, fetcher: BaseFetcher) -> None:
        """Register a fetcher instance by its source_name."""
        self._fetchers[fetcher.source_name.lower()] = fetcher

    def get(self, source_name: str) -> BaseFetcher | None:
        """Look up a fetcher by source name (case-insensitive)."""
        return self._fetchers.get(source_name.lower())

    def list_sources(self) -> list[str]:
        """Return all registered source names."""
        return list(self._fetchers.keys())

    def __len__(self) -> int:
        return len(self._fetchers)


# Global singleton - fetchers register themselves here on import
registry = FetcherRegistry()
