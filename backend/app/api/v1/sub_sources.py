"""Sub-sources API router - /api/v1/sub-sources endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.source import RatingIn, SubSourceCreate, SubSourceOut
from app.services import source_service

router = APIRouter(prefix="/sub-sources", tags=["sub-sources"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=list[SubSourceOut])
async def list_sub_sources(
    db: DbSession,
    source_id: int | None = Query(None, description="Filter by parent source"),
) -> list[SubSourceOut]:
    """List sub-sources, optionally filtered by source_id."""
    return await source_service.list_sub_sources(db, source_id=source_id)


@router.post("", response_model=SubSourceOut, status_code=201)
async def create_sub_source(
    db: DbSession,
    data: SubSourceCreate,
) -> SubSourceOut:
    """Add a new sub-source."""
    return await source_service.create_sub_source(db, data)


@router.patch("/{sub_source_id}/rate", response_model=SubSourceOut)
async def rate_sub_source(
    sub_source_id: int,
    body: RatingIn,
    db: DbSession,
) -> SubSourceOut:
    """Set user_rating (1-5) on a sub-source."""
    return await source_service.rate_sub_source(db, sub_source_id, body.rating)
