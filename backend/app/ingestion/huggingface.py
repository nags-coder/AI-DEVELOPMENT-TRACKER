"""Hugging Face fetcher - fetches daily papers + trending models."""

import contextlib
from datetime import datetime

import httpx

from app.ingestion.base import BaseFetcher, ContentItemCreate
from app.ingestion.registry import registry

PAPERS_URL = "https://huggingface.co/api/daily_papers"
MODELS_URL = "https://huggingface.co/api/models"
MAX_MODELS = 30


class HuggingFaceFetcher(BaseFetcher):
    """Fetches daily papers and trending models from Hugging Face APIs."""

    source_name = "Hugging Face"

    def __init__(self, max_models: int = MAX_MODELS):
        self.max_models = max_models

    async def fetch_raw(self) -> list[dict]:
        """Fetch both daily papers and trending models."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch daily papers
            papers_resp = await client.get(PAPERS_URL)
            papers_resp.raise_for_status()
            papers = papers_resp.json()

            # Fetch trending models
            models_resp = await client.get(
                MODELS_URL,
                params={
                    "sort": "trending",
                    "limit": str(self.max_models),
                },
            )
            models_resp.raise_for_status()
            models = models_resp.json()

        # Tag each item with its type for normalize()
        for p in papers:
            p["_hf_type"] = "paper"
        for m in models:
            m["_hf_type"] = "model"

        return papers + models

    def normalize(self, raw_item: dict) -> ContentItemCreate:
        """Convert a HF paper or model dict to ContentItemCreate."""
        hf_type = raw_item.get("_hf_type", "paper")

        if hf_type == "paper":
            return self._normalize_paper(raw_item)
        return self._normalize_model(raw_item)

    def _normalize_paper(self, raw: dict) -> ContentItemCreate:
        """Normalize a HF daily paper entry."""
        paper_data = raw.get("paper", raw)
        title = paper_data.get("title", "")
        summary = paper_data.get("summary", "") or ""
        if len(summary) > 500:
            summary = summary[:497] + "..."

        # Authors
        authors = paper_data.get("authors", [])
        if isinstance(authors, list):
            author_names = []
            for a in authors[:3]:
                if isinstance(a, dict):
                    author_names.append(a.get("name", str(a)))
                else:
                    author_names.append(str(a))
            author_str = ", ".join(author_names)
            if len(authors) > 3:
                author_str += " et al."
        else:
            author_str = str(authors)

        # Published date
        published_at = None
        pub_str = raw.get("publishedAt") or paper_data.get("publishedAt")
        if pub_str:
            with contextlib.suppress(ValueError):
                published_at = datetime.fromisoformat(pub_str.replace("Z", "+00:00")).replace(
                    tzinfo=None
                )

        # URL
        paper_id = paper_data.get("id", "")
        url = f"https://huggingface.co/papers/{paper_id}" if paper_id else ""

        tags = paper_data.get("tags", []) or []

        return ContentItemCreate(
            title=title,
            original_url=url,
            content_type="paper",
            source_name=self.source_name,
            summary=summary,
            author=author_str,
            published_at=published_at,
            topic_tags=tags[:10],
            engagement_score=raw.get("upvotes", 0) or 0,
        )

    def _normalize_model(self, raw: dict) -> ContentItemCreate:
        """Normalize a HF trending model entry."""
        model_id = raw.get("modelId") or raw.get("id", "")
        title = model_id

        # Use pipeline_tag or tags for topic tags
        tags = raw.get("tags", []) or []
        pipeline_tag = raw.get("pipeline_tag")
        if pipeline_tag and pipeline_tag not in tags:
            tags = [pipeline_tag, *tags]

        # Summary from card data or first tag
        summary = None
        card_data = raw.get("cardData", {}) or {}
        if isinstance(card_data, dict):
            summary = card_data.get("description")

        # Author (organization or user)
        author = model_id.split("/")[0] if "/" in model_id else ""

        # Downloads as engagement
        downloads = raw.get("downloads", 0) or 0

        # Published date
        published_at = None
        created_str = raw.get("createdAt") or raw.get("lastModified")
        if created_str:
            with contextlib.suppress(ValueError):
                published_at = datetime.fromisoformat(created_str.replace("Z", "+00:00")).replace(
                    tzinfo=None
                )

        url = f"https://huggingface.co/{model_id}" if model_id else ""

        return ContentItemCreate(
            title=title,
            original_url=url,
            content_type="model",
            source_name=self.source_name,
            summary=summary,
            author=author,
            published_at=published_at,
            topic_tags=tags[:10],
            engagement_score=downloads,
        )


# Auto-register on import
registry.register(HuggingFaceFetcher())
