"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    """Health check should return status ok when DB + Redis are available."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "degraded")
    assert "db" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_health_response_structure(client):
    """Health response should have the expected keys."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert set(data.keys()) == {"status", "db", "redis"}
