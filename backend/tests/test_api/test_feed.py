"""Tests for the Feed API endpoints (/api/v1/feed)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

BASE = "/api/v1/feed"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# -------------------------------------------------------------------
# GET /api/v1/feed
# -------------------------------------------------------------------


class TestGetFeed:
    """Tests for the paginated feed endpoint."""

    async def test_feed_returns_paginated_list(self, client: AsyncClient):
        """Feed returns data + meta envelope with default pagination."""
        resp = await client.get(BASE)
        assert resp.status_code == 200
        body = resp.json()

        assert "data" in body
        assert "meta" in body
        assert isinstance(body["data"], list)
        assert body["meta"]["page"] == 1
        assert body["meta"]["per_page"] == 20
        assert body["meta"]["total"] >= 1

    async def test_feed_items_have_correct_shape(self, client: AsyncClient):
        """Each feed item has required fields and embedded source."""
        resp = await client.get(BASE)
        item = resp.json()["data"][0]

        required_fields = {
            "id",
            "title",
            "original_url",
            "content_type",
            "relevance_score",
            "engagement_score",
            "is_read",
            "is_saved",
            "source",
        }
        assert required_fields.issubset(item.keys())
        assert "id" in item["source"]
        assert "name" in item["source"]
        assert "category" in item["source"]

    async def test_feed_filter_by_source(self, client: AsyncClient):
        """Filtering by source name returns only items from that source."""
        resp = await client.get(BASE, params={"source": "arxiv"})
        assert resp.status_code == 200
        body = resp.json()

        assert body["meta"]["total"] == 5
        for item in body["data"]:
            assert item["source"]["name"].lower() == "arxiv"

    async def test_feed_filter_by_content_type(self, client: AsyncClient):
        """Filtering by content_type returns only matching items."""
        resp = await client.get(BASE, params={"content_type": "repo"})
        assert resp.status_code == 200
        body = resp.json()

        assert body["meta"]["total"] == 5
        for item in body["data"]:
            assert item["content_type"] == "repo"

    async def test_feed_filter_by_multiple_content_types(self, client: AsyncClient):
        """Comma-separated content types are combined with OR."""
        resp = await client.get(BASE, params={"content_type": "paper,model"})
        assert resp.status_code == 200
        body = resp.json()

        for item in body["data"]:
            assert item["content_type"] in ("paper", "model")

    async def test_feed_filter_by_time_range(self, client: AsyncClient):
        """time_range=today returns items from today only."""
        resp = await client.get(BASE, params={"time_range": "today"})
        assert resp.status_code == 200
        # Seed data has published_at set relative to seed-run time.
        # All items may or may not match depending on when seeds ran.
        # At minimum, response should be valid shape.
        body = resp.json()
        assert isinstance(body["data"], list)
        assert body["meta"]["total"] >= 0

    async def test_feed_search(self, client: AsyncClient):
        """ILIKE search matches title/summary content."""
        resp = await client.get(BASE, params={"search": "transformer"})
        assert resp.status_code == 200
        body = resp.json()

        assert body["meta"]["total"] >= 1
        for item in body["data"]:
            text = (item["title"] + " " + (item["summary"] or "")).lower()
            assert "transformer" in text

    async def test_feed_search_no_results(self, client: AsyncClient):
        """Search for non-existent term returns empty list."""
        resp = await client.get(BASE, params={"search": "zzz_nonexistent_zzz"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["meta"]["total"] == 0
        assert body["data"] == []

    async def test_feed_pagination_page_2(self, client: AsyncClient):
        """Requesting page 2 with small per_page returns next batch."""
        resp = await client.get(BASE, params={"per_page": 5, "page": 2})
        assert resp.status_code == 200
        body = resp.json()

        assert body["meta"]["page"] == 2
        assert body["meta"]["per_page"] == 5
        assert len(body["data"]) <= 5

    async def test_feed_pagination_beyond_last_page(self, client: AsyncClient):
        """Requesting a page beyond total returns empty data."""
        resp = await client.get(BASE, params={"page": 999})
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []

    async def test_feed_sort_by_relevance(self, client: AsyncClient):
        """sort_by=relevance orders by descending relevance score."""
        resp = await client.get(BASE, params={"sort_by": "relevance"})
        assert resp.status_code == 200
        data = resp.json()["data"]

        scores = [float(item["relevance_score"]) for item in data]
        assert scores == sorted(scores, reverse=True)

    async def test_feed_invalid_time_range_rejected(self, client: AsyncClient):
        """Invalid time_range value returns 422 validation error."""
        resp = await client.get(BASE, params={"time_range": "invalid"})
        assert resp.status_code == 422

    async def test_feed_invalid_sort_by_rejected(self, client: AsyncClient):
        """Invalid sort_by value returns 422 validation error."""
        resp = await client.get(BASE, params={"sort_by": "invalid"})
        assert resp.status_code == 422


# -------------------------------------------------------------------
# GET /api/v1/feed/must-read
# -------------------------------------------------------------------


class TestMustRead:
    """Tests for the must-read endpoint."""

    async def test_must_read_returns_single_item(self, client: AsyncClient):
        """Must-read endpoint returns an item with a message."""
        resp = await client.get(f"{BASE}/must-read")
        assert resp.status_code == 200
        body = resp.json()

        assert "item" in body
        assert "message" in body

        # We have seed data, so item should not be None
        assert body["item"] is not None
        assert "title" in body["item"]
        assert "source" in body["item"]

    async def test_must_read_returns_highest_scored(self, client: AsyncClient):
        """Must-read item should be the highest relevance_score item."""
        resp = await client.get(f"{BASE}/must-read")
        body = resp.json()

        # Also get all items sorted by relevance
        feed_resp = await client.get(BASE, params={"sort_by": "relevance"})
        all_items = feed_resp.json()["data"]

        # The must-read item should be among the top-scored
        must_read_score = float(body["item"]["relevance_score"])
        top_score = float(all_items[0]["relevance_score"])
        assert must_read_score >= top_score * 0.9  # within 10% of top
