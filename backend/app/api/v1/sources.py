"""Sources API router - /api/v1/sources endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.source import (
    SourceCreate,
    SourceOut,
    SourceUpdate,
)
from app.services import source_service

router = APIRouter(prefix="/sources", tags=["sources"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[SourceOut])
async def list_sources(
    db: DbSession,
    status: str | None = Query(None, description="Filter by status: active, paused, retired"),
) -> list[SourceOut]:
    """List all sources, optionally filtered by status."""
    return await source_service.list_sources(db, status=status)


@router.post("", response_model=SourceOut, status_code=201)
async def create_source(
    db: DbSession,
    data: SourceCreate,
) -> SourceOut:
    """Add a new source."""
    return await source_service.create_source(db, data)


@router.patch("/{source_id}", response_model=SourceOut)
async def update_source(
    source_id: int,
    data: SourceUpdate,
    db: DbSession,
) -> SourceOut:
    """Partially update a source (changes are logged)."""
    return await source_service.update_source(db, source_id, data)


@router.delete("/{source_id}", response_model=SourceOut)
async def delete_source(
    source_id: int,
    db: DbSession,
) -> SourceOut:
    """Soft-delete a source (sets status to retired)."""
    return await source_service.soft_delete_source(db, source_id)
