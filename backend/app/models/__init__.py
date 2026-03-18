"""SQLAlchemy ORM models — import all models here for Alembic discovery."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


# Import all models so Alembic's autogenerate can detect them
from app.models.content_item import ContentItem  # noqa: E402, F401
from app.models.feedback import FeedbackLog  # noqa: E402, F401
from app.models.filter_preset import FilterPreset  # noqa: E402, F401
from app.models.source import Source  # noqa: E402, F401
from app.models.source_change_log import SourceChangeLog  # noqa: E402, F401
from app.models.sub_source import SubSource  # noqa: E402, F401
