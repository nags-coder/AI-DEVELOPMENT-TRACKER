"""Ingest API router - /api/v1/ingest endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ingestion.registry import registry

router = APIRouter(prefix="/ingest", tags=["ingestion"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


class TriggerResponse(BaseModel):
    status: str
    message: str
    registered_sources: list[str]


@router.post("/trigger", response_model=TriggerResponse, status_code=202)
async def trigger_ingest_all(db: DbSession) -> TriggerResponse:
    """Trigger ingestion for all active sources (async via Celery)."""
    from app.tasks.ingest import ingest_all_sources

    ingest_all_sources.delay()
    return TriggerResponse(
        status="accepted",
        message="Ingestion triggered for all active sources.",
        registered_sources=registry.list_sources(),
    )


@router.post("/trigger/{source_id}", status_code=202)
async def trigger_ingest_source(source_id: int, db: DbSession) -> dict:
    """Trigger ingestion for a single source by ID."""
    from app.tasks.ingest import ingest_source

    ingest_source.delay(source_id)
    return {
        "status": "accepted",
        "message": f"Ingestion triggered for source {source_id}.",
    }


@router.post("/score", status_code=202)
async def trigger_score_all(db: DbSession) -> dict:
    """Re-score all content items."""
    from app.scoring.ranker import score_all

    count = await score_all(db)
    return {
        "status": "ok",
        "message": f"Scored {count} content items.",
    }
