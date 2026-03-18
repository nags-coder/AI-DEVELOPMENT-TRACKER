"""SourceChangeLog model — audit trail for source edits."""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class SourceChangeLog(Base):
    __tablename__ = "source_change_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    field_changed: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, default=None)
    new_value: Mapped[str | None] = mapped_column(Text, default=None)
    reason: Mapped[str | None] = mapped_column(Text, default=None)
    changed_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="change_logs")  # noqa: F821

    __table_args__ = (Index("idx_changelog_source", "source_id"),)

    def __repr__(self) -> str:
        return f"<SourceChangeLog source={self.source_id} field={self.field_changed}>"
