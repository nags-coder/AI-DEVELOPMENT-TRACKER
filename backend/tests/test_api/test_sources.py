"""Tests for the Sources API endpoints (/api/v1/sources, /sub-sources)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

SOURCES_URL = "/api/v1/sources"
SUB_SOURCES_URL = "/api/v1/sub-sources"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestListSources:
    async def test_list_all_sources(self, client: AsyncClient):
        resp = await client.get(SOURCES_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3  # seeded sources

    async def test_list_sources_filter_by_status(self, client: AsyncClient):
        resp = await client.get(SOURCES_URL, params={"status": "active"})
        assert resp.status_code == 200
        for s in resp.json():
            assert s["status"] == "active"


class TestSourceCRUD:
    async def test_create_source(self, client: AsyncClient):
        payload = {
            "name": "Test New Source",
            "category": "X",
            "base_url": "https://example.com",
            "source_type": "api",
        }
        resp = await client.post(SOURCES_URL, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test New Source"
        assert data["status"] == "active"
        assert data["priority"] == 3  # default

    async def test_update_source(self, client: AsyncClient):
        # First, create a source to update
        create_resp = await client.post(
            SOURCES_URL,
            json={
                "name": "Update Test",
                "category": "X",
                "base_url": "https://example.com/update",
                "source_type": "manual",
            },
        )
        source_id = create_resp.json()["id"]

        resp = await client.patch(
            f"{SOURCES_URL}/{source_id}",
            json={"priority": 1, "notes": "updated"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["priority"] == 1
        assert data["notes"] == "updated"

    async def test_soft_delete_source(self, client: AsyncClient):
        create_resp = await client.post(
            SOURCES_URL,
            json={
                "name": "Delete Test",
                "category": "X",
                "base_url": "https://example.com/delete",
                "source_type": "rss",
            },
        )
        source_id = create_resp.json()["id"]

        resp = await client.delete(f"{SOURCES_URL}/{source_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "retired"

    async def test_update_nonexistent_source_returns_404(self, client: AsyncClient):
        resp = await client.patch(
            f"{SOURCES_URL}/99999",
            json={"notes": "test"},
        )
        assert resp.status_code == 404


class TestSubSources:
    async def test_list_sub_sources(self, client: AsyncClient):
        resp = await client.get(SUB_SOURCES_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 6  # seeded sub-sources

    async def test_list_sub_sources_filter_by_source(self, client: AsyncClient):
        resp = await client.get(SUB_SOURCES_URL, params={"source_id": 4})
        assert resp.status_code == 200
        for ss in resp.json():
            assert ss["source_id"] == 4

    async def test_create_sub_source(self, client: AsyncClient):
        # Use existing source_id 4 (arXiv)
        payload = {
            "source_id": 4,
            "platform": "arxiv",
            "handle": "cs.CL",
            "display_name": "Computation & Language",
        }
        resp = await client.post(SUB_SOURCES_URL, json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["handle"] == "cs.CL"
        assert data["source_id"] == 4

    async def test_rate_sub_source(self, client: AsyncClient):
        # Get first sub-source
        list_resp = await client.get(SUB_SOURCES_URL)
        sub_id = list_resp.json()[0]["id"]

        resp = await client.patch(
            f"{SUB_SOURCES_URL}/{sub_id}/rate",
            json={"rating": 5},
        )
        assert resp.status_code == 200
        assert resp.json()["user_rating"] == 5

    async def test_rate_nonexistent_sub_source_returns_404(self, client: AsyncClient):
        resp = await client.patch(
            f"{SUB_SOURCES_URL}/99999/rate",
            json={"rating": 3},
        )
        assert resp.status_code == 404
