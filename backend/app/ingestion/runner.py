"""Ingestion runner - orchestrates fetcher execution."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.base import IngestionResult
from app.ingestion.registry import registry
from app.models.source import Source


async def run_source(db: AsyncSession, source_id: int) -> IngestionResult | None:
    """Run the fetcher for a single source by ID."""
    source = await db.get(Source, source_id)
    if not source:
        return None

    fetcher = registry.get(source.name)
    if not fetcher:
        return IngestionResult(
            source=source.name,
            fetched=0,
            new=0,
            errors=[f"No fetcher registered for '{source.name}'"],
        )

    result = await fetcher.run(db, source.id)

    # Update last_checked timestamp
    from sqlalchemy import func

    source.last_checked = func.now()
    await db.flush()

    return result


async def run_all_sources(db: AsyncSession) -> list[IngestionResult]:
    """Run fetchers for all active sources that have a registered fetcher."""
    q = select(Source).where(Source.status == "active").order_by(Source.priority)
    result = await db.execute(q)
    sources = result.scalars().all()

    results: list[IngestionResult] = []
    for source in sources:
        r = await run_source(db, source.id)
        if r:
            results.append(r)

    return results
