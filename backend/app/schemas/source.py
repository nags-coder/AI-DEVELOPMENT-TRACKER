"""Source-related Pydantic schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SourceOut(BaseModel):
    """Full source detail returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    base_url: str
    source_type: str
    priority: int
    status: str
    user_rating: int | None = None
    quality_score: Decimal
    added_at: datetime
    last_checked: datetime | None = None
    notes: str | None = None


class SourceCreate(BaseModel):
    """Schema for creating a new source."""

    name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    base_url: str
    source_type: str = Field(..., max_length=30)
    priority: int = Field(3, ge=1, le=5)
    notes: str | None = None


class SourceUpdate(BaseModel):
    """Schema for partially updating a source. All fields optional."""

    name: str | None = Field(None, max_length=100)
    category: str | None = Field(None, max_length=50)
    base_url: str | None = None
    source_type: str | None = Field(None, max_length=30)
    priority: int | None = Field(None, ge=1, le=5)
    status: str | None = Field(None, pattern="^(active|paused|retired)$")
    user_rating: int | None = Field(None, ge=1, le=5)
    notes: str | None = None


class SubSourceOut(BaseModel):
    """Full sub-source detail."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int
    platform: str
    handle: str
    display_name: str | None = None
    user_rating: int | None = None
    status: str
    last_fetched: datetime | None = None
    content_count: int
    avg_quality: Decimal
    added_at: datetime


class SubSourceCreate(BaseModel):
    """Schema for creating a new sub-source."""

    source_id: int
    platform: str = Field(..., max_length=50)
    handle: str = Field(..., max_length=200)
    display_name: str | None = Field(None, max_length=200)


class RatingIn(BaseModel):
    """Schema for rating a sub-source."""

    rating: int = Field(..., ge=1, le=5)
