"""Feed API router - /api/v1/feed endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.feed import ContentItemOut, MustReadOut
from app.services import feed_service

router = APIRouter(prefix="/feed", tags=["feed"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=PaginatedResponse[ContentItemOut])
async def get_feed(
    db: DbSession,
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    source: str | None = Query(None, description="Comma-separated source names"),
    content_type: str | None = Query(None, description="Comma-separated content types"),
    time_range: str | None = Query(
        None,
        description="Time filter: today, 7d, 30d, or all",
        pattern="^(today|7d|30d|all)$",
    ),
    search: str | None = Query(None, max_length=200, description="Search query (ILIKE)"),
    sort_by: str = Query(
        "date",
        description="Sort order: date or relevance",
        pattern="^(date|relevance)$",
    ),
) -> PaginatedResponse[ContentItemOut]:
    """Return a paginated, filtered feed of content items."""
    return await feed_service.get_feed(
        db,
        page=page,
        per_page=per_page,
        source=source,
        content_type=content_type,
        time_range=time_range,
        search=search,
        sort_by=sort_by,
    )


@router.get("/must-read", response_model=MustReadOut)
async def get_must_read(
    db: DbSession,
) -> MustReadOut:
    """Return the single top-scored item you should read today."""
    return await feed_service.get_must_read(db)
