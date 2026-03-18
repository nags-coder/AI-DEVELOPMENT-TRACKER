"""Tests for the ingestion framework and ingest API."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.ingestion.base import BaseFetcher, ContentItemCreate, IngestionResult
from app.ingestion.registry import FetcherRegistry
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- Mock fetcher for testing ---


class MockFetcher(BaseFetcher):
    """A concrete fetcher for testing the BaseFetcher contract."""

    source_name = "mock_source"

    def __init__(self, items: list[dict] | None = None):
        self._items = items or []

    async def fetch_raw(self) -> list[dict]:
        return self._items

    def normalize(self, raw_item: dict) -> ContentItemCreate:
        return ContentItemCreate(
            title=raw_item["title"],
            original_url=raw_item["url"],
            content_type="paper",
            source_name=self.source_name,
            summary=raw_item.get("summary"),
        )


# --- BaseFetcher contract tests ---


class TestBaseFetcher:
    def test_mock_fetcher_has_source_name(self):
        f = MockFetcher()
        assert f.source_name == "mock_source"

    def test_normalize_returns_content_item_create(self):
        f = MockFetcher()
        item = f.normalize({"title": "Test", "url": "https://test.com"})
        assert isinstance(item, ContentItemCreate)
        assert item.title == "Test"
        assert item.original_url == "https://test.com"
        assert item.content_type == "paper"

    async def test_fetch_raw_returns_list(self):
        f = MockFetcher(items=[{"title": "A", "url": "https://a.com"}])
        raw = await f.fetch_raw()
        assert len(raw) == 1


# --- FetcherRegistry tests ---


class TestFetcherRegistry:
    def test_register_and_get(self):
        reg = FetcherRegistry()
        fetcher = MockFetcher()
        reg.register(fetcher)
        assert reg.get("mock_source") is fetcher

    def test_get_case_insensitive(self):
        reg = FetcherRegistry()
        reg.register(MockFetcher())
        assert reg.get("Mock_Source") is not None
        assert reg.get("MOCK_SOURCE") is not None

    def test_get_unknown_returns_none(self):
        reg = FetcherRegistry()
        assert reg.get("nonexistent") is None

    def test_list_sources(self):
        reg = FetcherRegistry()
        reg.register(MockFetcher())
        sources = reg.list_sources()
        assert "mock_source" in sources

    def test_len(self):
        reg = FetcherRegistry()
        assert len(reg) == 0
        reg.register(MockFetcher())
        assert len(reg) == 1


# --- IngestionResult ---


class TestIngestionResult:
    def test_result_fields(self):
        r = IngestionResult(source="test", fetched=10, new=5)
        assert r.source == "test"
        assert r.fetched == 10
        assert r.new == 5
        assert r.errors == []


# --- Ingest API endpoint tests ---


class TestIngestAPI:
    async def test_trigger_all_returns_202(self, client: AsyncClient):
        """POST /api/v1/ingest/trigger returns 202 Accepted."""
        resp = await client.post("/api/v1/ingest/trigger")
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "accepted"
        assert "registered_sources" in data

    async def test_trigger_single_returns_202(self, client: AsyncClient):
        """POST /api/v1/ingest/trigger/{id} returns 202 Accepted."""
        resp = await client.post("/api/v1/ingest/trigger/4")
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "accepted"
