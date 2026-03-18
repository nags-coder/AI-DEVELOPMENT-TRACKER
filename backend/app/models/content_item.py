"""ContentItem model — individual pieces of content (paper, repo, model, etc.)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    ARRAY,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    sub_source_id: Mapped[int | None] = mapped_column(ForeignKey("sub_sources.id"), default=None)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, default=None)
    original_url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    author: Mapped[str | None] = mapped_column(String(300), default=None)
    published_at: Mapped[datetime | None] = mapped_column(default=None)
    fetched_at: Mapped[datetime] = mapped_column(default=func.now())
    content_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # paper, repo, model, etc.
    thumbnail_url: Mapped[str | None] = mapped_column(Text, default=None)
    topic_tags: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    relevance_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.0000"))
    engagement_score: Mapped[int] = mapped_column(Integer, default=0)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_saved: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback: Mapped[str | None] = mapped_column(String(10), default=None)  # up, down, or null

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="content_items")  # noqa: F821
    sub_source: Mapped["SubSource | None"] = relationship(  # noqa: F821
        back_populates="content_items"
    )
    feedback_logs: Mapped[list["FeedbackLog"]] = relationship(  # noqa: F821
        back_populates="content_item", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_content_source", "source_id"),
        Index("idx_content_sub_source", "sub_source_id"),
        Index("idx_content_published", published_at.desc()),
        Index("idx_content_relevance", relevance_score.desc()),
        Index("idx_content_type", "content_type"),
        Index("idx_content_tags", "topic_tags", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        return f"<ContentItem {self.content_type}: {self.title[:50]}>"
