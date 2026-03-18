"""Tests for the Content API endpoints (/api/v1/content)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

CONTENT_URL = "/api/v1/content"


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestContentDetail:
    async def test_get_content_item(self, client: AsyncClient):
        resp = await client.get(f"{CONTENT_URL}/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert "title" in data
        assert "source" in data

    async def test_get_nonexistent_content_returns_404(self, client: AsyncClient):
        resp = await client.get(f"{CONTENT_URL}/99999")
        assert resp.status_code == 404


class TestFeedback:
    async def test_submit_upvote(self, client: AsyncClient):
        resp = await client.post(
            f"{CONTENT_URL}/1/feedback",
            json={"action": "up"},
        )
        assert resp.status_code == 200
        assert resp.json()["feedback"] == "up"

    async def test_submit_downvote(self, client: AsyncClient):
        resp = await client.post(
            f"{CONTENT_URL}/2/feedback",
            json={"action": "down"},
        )
        assert resp.status_code == 200
        assert resp.json()["feedback"] == "down"

    async def test_invalid_feedback_action(self, client: AsyncClient):
        resp = await client.post(
            f"{CONTENT_URL}/1/feedback",
            json={"action": "invalid"},
        )
        assert resp.status_code == 422

    async def test_feedback_on_nonexistent_item(self, client: AsyncClient):
        resp = await client.post(
            f"{CONTENT_URL}/99999/feedback",
            json={"action": "up"},
        )
        assert resp.status_code == 404


class TestBookmarks:
    async def test_save_content(self, client: AsyncClient):
        resp = await client.post(f"{CONTENT_URL}/3/save")
        assert resp.status_code == 200
        assert resp.json()["is_saved"] is True

    async def test_unsave_content(self, client: AsyncClient):
        # First save, then unsave
        await client.post(f"{CONTENT_URL}/4/save")
        resp = await client.delete(f"{CONTENT_URL}/4/save")
        assert resp.status_code == 200
        assert resp.json()["is_saved"] is False

    async def test_save_nonexistent_item(self, client: AsyncClient):
        resp = await client.post(f"{CONTENT_URL}/99999/save")
        assert resp.status_code == 404
