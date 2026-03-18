"""Feed-related Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SourceBrief(BaseModel):
    """Minimal source info embedded in feed items."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str


class ContentItemOut(BaseModel):
    """Schema for a single content item in the feed response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str | None = None
    original_url: str
    author: str | None = None
    published_at: datetime | None = None
    content_type: str
    thumbnail_url: str | None = None
    topic_tags: list[str] = []
    relevance_score: Decimal
    engagement_score: int
    is_read: bool
    is_saved: bool
    feedback: str | None = None
    source: SourceBrief


class MustReadOut(BaseModel):
    """Schema for the single must-read item response."""

    item: ContentItemOut | None = None
    message: str = "Here's what you should read today."
