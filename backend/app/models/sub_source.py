"""SubSource model — accounts/channels within a platform."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class SubSource(Base):
    __tablename__ = "sub_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # arxiv, github, huggingface
    handle: Mapped[str] = mapped_column(
        String(200), nullable=False
    )  # subreddit, username, category
    display_name: Mapped[str | None] = mapped_column(String(200), default=None)
    user_rating: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5
    status: Mapped[str] = mapped_column(String(20), default="active")
    last_fetched: Mapped[datetime | None] = mapped_column(default=None)
    content_count: Mapped[int] = mapped_column(default=0)
    avg_quality: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.00"))
    added_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="sub_sources")  # noqa: F821
    content_items: Mapped[list["ContentItem"]] = relationship(  # noqa: F821
        back_populates="sub_source"
    )

    __table_args__ = (
        UniqueConstraint("source_id", "handle", name="uq_sub_source_handle"),
        Index("idx_sub_sources_source", "source_id"),
        Index("idx_sub_sources_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<SubSource {self.platform}/{self.handle}>"
