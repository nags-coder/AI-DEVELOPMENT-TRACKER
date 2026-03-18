"""Content service - feedback, bookmarks, detail retrieval."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content_item import ContentItem
from app.models.feedback import FeedbackLog
from app.schemas.feed import ContentItemOut


async def get_content_item(db: AsyncSession, content_id: int) -> ContentItem:
    """Fetch a content item with source loaded, or raise 404."""
    q = (
        select(ContentItem)
        .options(selectinload(ContentItem.source))
        .where(ContentItem.id == content_id)
    )
    result = await db.execute(q)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    return item


async def get_content_detail(db: AsyncSession, content_id: int) -> ContentItemOut:
    """Return a single content item as schema."""
    item = await get_content_item(db, content_id)
    return ContentItemOut.model_validate(item)


async def submit_feedback(db: AsyncSession, content_id: int, action: str) -> ContentItemOut:
    """Record feedback (up/down) on a content item."""
    item = await get_content_item(db, content_id)
    item.feedback = action
    db.add(FeedbackLog(content_id=item.id, action=action))
    await db.flush()
    await db.refresh(item)
    return ContentItemOut.model_validate(item)


async def toggle_save(db: AsyncSession, content_id: int, *, save: bool) -> ContentItemOut:
    """Set or clear the is_saved flag on a content item."""
    item = await get_content_item(db, content_id)
    item.is_saved = save
    await db.flush()
    await db.refresh(item)
    return ContentItemOut.model_validate(item)
