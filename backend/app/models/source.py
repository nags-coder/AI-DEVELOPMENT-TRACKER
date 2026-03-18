"""Source model — represents a top-level content platform (e.g., arXiv, GitHub)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Index, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)  # api, rss, scrape, manual
    priority: Mapped[int] = mapped_column(SmallInteger, default=3)  # 1 (highest) to 5 (lowest)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, paused, retired
    user_rating: Mapped[int | None] = mapped_column(SmallInteger)  # 1-5
    quality_score: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0.00"))
    added_at: Mapped[datetime] = mapped_column(default=func.now())
    last_checked: Mapped[datetime | None] = mapped_column(default=None)
    notes: Mapped[str | None] = mapped_column(Text, default=None)

    # Relationships
    sub_sources: Mapped[list["SubSource"]] = relationship(  # noqa: F821
        back_populates="source", cascade="all, delete-orphan"
    )
    content_items: Mapped[list["ContentItem"]] = relationship(  # noqa: F821
        back_populates="source"
    )
    change_logs: Mapped[list["SourceChangeLog"]] = relationship(  # noqa: F821
        back_populates="source", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_sources_status", "status"),
        Index("idx_sources_category", "category"),
    )

    def __repr__(self) -> str:
        return f"<Source {self.name} [{self.status}]>"
