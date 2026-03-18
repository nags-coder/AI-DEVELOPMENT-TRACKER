"""Content API router - /api/v1/content endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.content import FeedbackIn
from app.schemas.feed import ContentItemOut
from app.services import content_service

router = APIRouter(prefix="/content", tags=["content"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/{content_id}", response_model=ContentItemOut)
async def get_content(
    content_id: int,
    db: DbSession,
) -> ContentItemOut:
    """Get a single content item by ID."""
    return await content_service.get_content_detail(db, content_id)


@router.post("/{content_id}/feedback", response_model=ContentItemOut)
async def submit_feedback(
    content_id: int,
    body: FeedbackIn,
    db: DbSession,
) -> ContentItemOut:
    """Submit up/down feedback on a content item."""
    return await content_service.submit_feedback(db, content_id, body.action)


@router.post("/{content_id}/save", response_model=ContentItemOut)
async def save_content(
    content_id: int,
    db: DbSession,
) -> ContentItemOut:
    """Bookmark a content item."""
    return await content_service.toggle_save(db, content_id, save=True)


@router.delete("/{content_id}/save", response_model=ContentItemOut)
async def unsave_content(
    content_id: int,
    db: DbSession,
) -> ContentItemOut:
    """Remove bookmark from a content item."""
    return await content_service.toggle_save(db, content_id, save=False)
