"""Content-related Pydantic schemas (feedback, bookmarks)."""

from pydantic import BaseModel, Field


class FeedbackIn(BaseModel):
    """Schema for submitting feedback on a content item."""

    action: str = Field(..., pattern="^(up|down)$")
