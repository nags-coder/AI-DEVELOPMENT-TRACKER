"""Source service - CRUD operations for sources and sub-sources."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.models.source_change_log import SourceChangeLog
from app.models.sub_source import SubSource
from app.schemas.source import (
    SourceCreate,
    SourceOut,
    SourceUpdate,
    SubSourceCreate,
    SubSourceOut,
)


async def list_sources(
    db: AsyncSession,
    *,
    status: str | None = None,
) -> list[SourceOut]:
    """Return all sources, optionally filtered by status."""
    q = select(Source).order_by(Source.priority, Source.name)
    if status:
        q = q.where(Source.status == status)
    result = await db.execute(q)
    return [SourceOut.model_validate(s) for s in result.scalars().all()]


async def create_source(db: AsyncSession, data: SourceCreate) -> SourceOut:
    """Create a new source."""
    source = Source(**data.model_dump())
    db.add(source)
    await db.flush()
    await db.refresh(source)
    return SourceOut.model_validate(source)


async def get_source(db: AsyncSession, source_id: int) -> Source:
    """Fetch a single source or raise 404."""
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


async def update_source(db: AsyncSession, source_id: int, data: SourceUpdate) -> SourceOut:
    """Partially update a source and log changes."""
    source = await get_source(db, source_id)
    updates = data.model_dump(exclude_unset=True)

    for field, new_value in updates.items():
        old_value = getattr(source, field)
        if str(old_value) != str(new_value):
            db.add(
                SourceChangeLog(
                    source_id=source.id,
                    field_changed=field,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                    reason="user_update",
                )
            )
        setattr(source, field, new_value)

    await db.flush()
    await db.refresh(source)
    return SourceOut.model_validate(source)


async def soft_delete_source(db: AsyncSession, source_id: int) -> SourceOut:
    """Soft-delete a source by setting status to 'retired'."""
    source = await get_source(db, source_id)
    source.status = "retired"
    db.add(
        SourceChangeLog(
            source_id=source.id,
            field_changed="status",
            old_value=source.status,
            new_value="retired",
            reason="user_delete",
        )
    )
    await db.flush()
    await db.refresh(source)
    return SourceOut.model_validate(source)


# --- Sub-sources ---


async def list_sub_sources(
    db: AsyncSession,
    *,
    source_id: int | None = None,
) -> list[SubSourceOut]:
    """List sub-sources, optionally filtered by source_id."""
    q = select(SubSource).order_by(SubSource.platform, SubSource.handle)
    if source_id is not None:
        q = q.where(SubSource.source_id == source_id)
    result = await db.execute(q)
    return [SubSourceOut.model_validate(ss) for ss in result.scalars().all()]


async def create_sub_source(db: AsyncSession, data: SubSourceCreate) -> SubSourceOut:
    """Create a new sub-source."""
    # Validate parent source exists
    await get_source(db, data.source_id)
    sub = SubSource(**data.model_dump())
    db.add(sub)
    await db.flush()
    await db.refresh(sub)
    return SubSourceOut.model_validate(sub)


async def rate_sub_source(db: AsyncSession, sub_source_id: int, rating: int) -> SubSourceOut:
    """Set user_rating on a sub-source."""
    sub = await db.get(SubSource, sub_source_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Sub-source not found")
    sub.user_rating = rating
    await db.flush()
    await db.refresh(sub)
    return SubSourceOut.model_validate(sub)
