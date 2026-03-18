"""Celery tasks for content ingestion."""

import asyncio
from dataclasses import asdict

from app.database import async_session_factory
from app.ingestion.runner import run_all_sources, run_source
from app.tasks.celery_app import celery_app


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.tasks.ingest.ingest_all_sources")
def ingest_all_sources():
    """Celery task: ingest content from all active sources."""

    async def _run():
        async with async_session_factory() as db:
            try:
                results = await run_all_sources(db)
                await db.commit()
                return [asdict(r) for r in results]
            except Exception:
                await db.rollback()
                raise

    return _run_async(_run())


@celery_app.task(name="app.tasks.ingest.ingest_source")
def ingest_source(source_id: int):
    """Celery task: ingest content from a single source."""

    async def _run():
        async with async_session_factory() as db:
            try:
                result = await run_source(db, source_id)
                await db.commit()
                return asdict(result) if result else None
            except Exception:
                await db.rollback()
                raise

    return _run_async(_run())
