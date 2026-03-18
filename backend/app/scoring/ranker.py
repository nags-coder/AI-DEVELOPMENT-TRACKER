"""Scoring engine - computes relevance_score for content items.

MVP formula:
    score = 0.4*recency + 0.3*quality + 0.2*engagement + 0.1*type_boost

All component scores are normalized to 0.0-1.0.
"""

import math
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_item import ContentItem
from app.models.source import Source

# Content type weights (higher = more valuable in the feed)
TYPE_WEIGHTS: dict[str, float] = {
    "paper": 0.8,
    "repo": 0.7,
    "model": 0.6,
    "space": 0.5,
    "dataset": 0.5,
    "blog": 0.4,
    "video": 0.4,
    "news": 0.3,
}

# Scoring weights
W_RECENCY = 0.4
W_QUALITY = 0.3
W_ENGAGEMENT = 0.2
W_TYPE = 0.1

# Engagement cap (items with >= this score get engagement=1.0)
ENGAGEMENT_CAP = 10000

# Recency half-life in days (score halves every N days)
RECENCY_HALF_LIFE = 3.0


def recency_score(published_at: datetime | None, now: datetime | None = None) -> float:
    """Exponential decay based on age. Today=1.0, halves every HALF_LIFE days.

    Returns 0.0 for items older than 30 days or with no published_at.
    """
    if published_at is None:
        return 0.0

    if now is None:
        now = datetime.now()

    age_hours = max(0, (now - published_at).total_seconds() / 3600)
    age_days = age_hours / 24

    if age_days > 30:
        return 0.0

    # Exponential decay: score = 2^(-age_days / half_life)
    return math.pow(2, -age_days / RECENCY_HALF_LIFE)


def quality_score(user_rating: int | None) -> float:
    """Normalize source user_rating (1-5) to 0.0-1.0. Default=3 if unrated."""
    rating = user_rating if user_rating is not None else 3
    return max(0.0, min(rating / 5.0, 1.0))


def engagement_normalized(engagement_score: int) -> float:
    """Normalize engagement (stars, downloads, etc.) to 0.0-1.0 with cap."""
    if engagement_score <= 0:
        return 0.0
    return min(engagement_score / ENGAGEMENT_CAP, 1.0)


def type_boost(content_type: str) -> float:
    """Return the type weight for the given content type."""
    return TYPE_WEIGHTS.get(content_type, 0.5)


def score_item(
    item: ContentItem,
    source: Source,
    now: datetime | None = None,
) -> float:
    """Compute the relevance score for a single content item.

    Returns a float in [0.0, 1.0].
    """
    r = recency_score(item.published_at, now)
    q = quality_score(source.user_rating)
    e = engagement_normalized(item.engagement_score)
    t = type_boost(item.content_type)

    raw = (W_RECENCY * r) + (W_QUALITY * q) + (W_ENGAGEMENT * e) + (W_TYPE * t)
    return round(max(0.0, min(raw, 1.0)), 4)


async def score_all(db: AsyncSession) -> int:
    """Re-score all content items in the database. Returns count scored."""
    q = select(ContentItem, Source).join(Source, ContentItem.source_id == Source.id)
    result = await db.execute(q)
    rows = result.all()

    count = 0
    now = datetime.now()
    for item, source in rows:
        new_score = score_item(item, source, now)
        item.relevance_score = Decimal(str(new_score))
        count += 1

    if count:
        await db.flush()

    return count
