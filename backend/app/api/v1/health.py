"""Health check endpoint."""

import redis.asyncio as aioredis
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import async_session_factory

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check():
    """Check DB and Redis connectivity."""
    db_ok = False
    redis_ok = False

    # Check PostgreSQL
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    # Check Redis
    try:
        r = aioredis.from_url(settings.REDIS_URL)
        pong = await r.ping()
        redis_ok = pong is True
        await r.aclose()
    except Exception:
        pass

    status = "ok" if (db_ok and redis_ok) else "degraded"
    return {"status": status, "db": db_ok, "redis": redis_ok}
