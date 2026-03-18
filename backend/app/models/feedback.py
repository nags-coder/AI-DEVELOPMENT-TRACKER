"""FeedbackLog model — tracks user thumbs-up/down actions."""

from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


class FeedbackLog(Base):
    __tablename__ = "feedback_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(10), nullable=False)  # up or down
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    content_item: Mapped["ContentItem"] = relationship(  # noqa: F821
        back_populates="feedback_logs"
    )

    __table_args__ = (
        Index("idx_feedback_content", "content_id"),
        Index("idx_feedback_created", created_at.desc()),
    )

    def __repr__(self) -> str:
        return f"<FeedbackLog content={self.content_id} action={self.action}>"
