"""Test fixtures."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop_policy():
    """Use default event loop policy (required by pytest-asyncio >= 1.0)."""
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(loop_scope="session")
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
