"""Base fetcher ABC - defines the contract for all source fetchers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_item import ContentItem


@dataclass
class ContentItemCreate:
    """Intermediate representation of a content item before DB insertion."""

    title: str
    original_url: str
    content_type: str
    source_name: str  # resolved to source_id at upsert time
    summary: str | None = None
    author: str | None = None
    published_at: datetime | None = None
    thumbnail_url: str | None = None
    topic_tags: list[str] = field(default_factory=list)
    engagement_score: int = 0
    sub_source_handle: str | None = None  # resolved to sub_source_id at upsert


@dataclass
class IngestionResult:
    """Summary of a single fetcher run."""

    source: str
    fetched: int
    new: int
    errors: list[str] = field(default_factory=list)


class BaseFetcher(ABC):
    """Abstract base class for all source fetchers.

    Subclasses must implement fetch_raw() and normalize().
    The run() method provides the full pipeline: fetch -> normalize -> deduplicate -> upsert.
    """

    source_name: str = ""

    @abstractmethod
    async def fetch_raw(self) -> list[dict]:
        """Fetch raw data from the external source API.

        Returns a list of raw dicts that will be normalized.
        """
        ...

    @abstractmethod
    def normalize(self, raw_item: dict) -> ContentItemCreate:
        """Convert a single raw API response dict to ContentItemCreate."""
        ...

    async def run(self, db: AsyncSession, source_id: int) -> IngestionResult:
        """Full pipeline: fetch -> normalize -> deduplicate -> upsert."""
        raw_items = await self.fetch_raw()
        normalized = []
        errors: list[str] = []

        for raw in raw_items:
            try:
                normalized.append(self.normalize(raw))
            except Exception as e:
                errors.append(f"Normalize error: {e}")

        new_count = await self._upsert_deduped(db, normalized, source_id)
        return IngestionResult(
            source=self.source_name,
            fetched=len(raw_items),
            new=new_count,
            errors=errors,
        )

    async def _upsert_deduped(
        self,
        db: AsyncSession,
        items: list[ContentItemCreate],
        source_id: int,
    ) -> int:
        """Insert only items whose original_url doesn't already exist."""
        if not items:
            return 0

        urls = [item.original_url for item in items]
        existing_q = select(ContentItem.original_url).where(ContentItem.original_url.in_(urls))
        result = await db.execute(existing_q)
        existing_urls = {row[0] for row in result.all()}

        new_count = 0
        for item in items:
            if item.original_url in existing_urls:
                continue
            db.add(
                ContentItem(
                    source_id=source_id,
                    title=item.title,
                    summary=item.summary,
                    original_url=item.original_url,
                    author=item.author,
                    published_at=item.published_at,
                    content_type=item.content_type,
                    thumbnail_url=item.thumbnail_url,
                    topic_tags=item.topic_tags,
                    engagement_score=item.engagement_score,
                )
            )
            new_count += 1

        if new_count:
            await db.flush()

        return new_count
