"""Feed service — builds dynamic queries with filtering, search, and pagination."""

import math
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content_item import ContentItem
from app.models.source import Source
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.feed import ContentItemOut, MustReadOut

# Valid time-range shortcuts
TIME_RANGES: dict[str, timedelta] = {
    "today": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


async def get_feed(
    db: AsyncSession,
    *,
    page: int = 1,
    per_page: int = 20,
    source: str | None = None,
    content_type: str | None = None,
    time_range: str | None = None,
    search: str | None = None,
    sort_by: str = "date",
) -> PaginatedResponse[ContentItemOut]:
    """Return a paginated, filtered feed of content items.

    Parameters
    ----------
    db : AsyncSession
    page : int - 1-based page number
    per_page : int - items per page (clamped to 1-100)
    source : str | None - comma-separated source names to include
    content_type : str | None - comma-separated content types to include
    time_range : str | None - today / 7d / 30d / all
    search : str | None - full-text search query
    sort_by : str - "relevance" or "date" (default)
    """
    per_page = max(1, min(per_page, 100))

    # Base query - eager-load source for serialisation
    base = select(ContentItem).options(selectinload(ContentItem.source))

    # --- Filters ---
    if source:
        names = [n.strip().lower() for n in source.split(",") if n.strip()]
        base = base.join(Source, ContentItem.source_id == Source.id).where(
            func.lower(Source.name).in_(names)
        )

    if content_type:
        types = [t.strip().lower() for t in content_type.split(",") if t.strip()]
        base = base.where(func.lower(ContentItem.content_type).in_(types))

    if time_range and time_range in TIME_RANGES:
        cutoff = datetime.now() - TIME_RANGES[time_range]
        base = base.where(ContentItem.published_at >= cutoff)

    if search:
        # Simple ILIKE search (no FTS vector column yet — will upgrade later)
        pattern = f"%{search}%"
        base = base.where(ContentItem.title.ilike(pattern) | ContentItem.summary.ilike(pattern))

    # --- Count total ---
    count_q = select(func.count()).select_from(base.subquery())
    total_result = await db.execute(count_q)
    total = total_result.scalar_one()

    # --- Ordering ---
    if sort_by == "relevance":
        base = base.order_by(ContentItem.relevance_score.desc(), ContentItem.published_at.desc())
    else:
        base = base.order_by(ContentItem.published_at.desc(), ContentItem.relevance_score.desc())

    # --- Pagination ---
    offset = (page - 1) * per_page
    base = base.offset(offset).limit(per_page)

    result = await db.execute(base)
    items = result.unique().scalars().all()

    total_pages = math.ceil(total / per_page) if total else 0

    return PaginatedResponse[ContentItemOut](
        data=[ContentItemOut.model_validate(item) for item in items],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
        ),
    )


async def get_must_read(db: AsyncSession) -> MustReadOut:
    """Return the single highest-scoring item published today (or recently)."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    q = (
        select(ContentItem)
        .options(selectinload(ContentItem.source))
        .where(ContentItem.published_at >= today_start)
        .order_by(ContentItem.relevance_score.desc())
        .limit(1)
    )
    result = await db.execute(q)
    item = result.unique().scalars().first()

    if item is None:
        # Fallback: highest-scoring item in the last 7 days
        fallback_cutoff = datetime.now() - timedelta(days=7)
        q = (
            select(ContentItem)
            .options(selectinload(ContentItem.source))
            .where(ContentItem.published_at >= fallback_cutoff)
            .order_by(ContentItem.relevance_score.desc())
            .limit(1)
        )
        result = await db.execute(q)
        item = result.unique().scalars().first()

    if item is None:
        return MustReadOut(item=None, message="No recent items found.")

    return MustReadOut(
        item=ContentItemOut.model_validate(item),
        message="Here's what you should read today.",
    )
