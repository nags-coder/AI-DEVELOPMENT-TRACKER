"""ArXiv fetcher - fetches recent AI papers from the arXiv API."""

import contextlib
import xml.etree.ElementTree as ET
from datetime import datetime

import httpx

from app.ingestion.base import BaseFetcher, ContentItemCreate
from app.ingestion.registry import registry

# arXiv Atom feed namespaces
ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_NS = "http://arxiv.org/schemas/atom"

# AI-related categories to search
CATEGORIES = ["cs.AI", "cs.LG", "cs.CL"]
MAX_RESULTS = 50


class ArxivFetcher(BaseFetcher):
    """Fetches recent papers from arXiv's Atom API."""

    source_name = "arXiv"

    def __init__(self, max_results: int = MAX_RESULTS):
        self.max_results = max_results
        self.base_url = "http://export.arxiv.org/api/query"

    async def fetch_raw(self) -> list[dict]:
        """Fetch raw entries from arXiv Atom feed."""
        cat_query = "+OR+".join(f"cat:{c}" for c in CATEGORIES)
        params = {
            "search_query": cat_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": str(self.max_results),
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(self.base_url, params=params)
            resp.raise_for_status()

        return self._parse_atom(resp.text)

    def _parse_atom(self, xml_text: str) -> list[dict]:
        """Parse arXiv Atom XML into a list of dicts."""
        root = ET.fromstring(xml_text)
        entries = []

        for entry in root.findall(f"{{{ATOM_NS}}}entry"):
            title = (entry.findtext(f"{{{ATOM_NS}}}title") or "").strip()
            summary = (entry.findtext(f"{{{ATOM_NS}}}summary") or "").strip()

            # Truncate summary to first ~500 chars
            if len(summary) > 500:
                summary = summary[:497] + "..."

            # Authors (first 3)
            authors = []
            for author_el in entry.findall(f"{{{ATOM_NS}}}author")[:3]:
                name = author_el.findtext(f"{{{ATOM_NS}}}name")
                if name:
                    authors.append(name.strip())
            author_str = ", ".join(authors)
            if len(entry.findall(f"{{{ATOM_NS}}}author")) > 3:
                author_str += " et al."

            # Published date
            published_str = entry.findtext(f"{{{ATOM_NS}}}published") or ""
            published_at = None
            if published_str:
                with contextlib.suppress(ValueError):
                    published_at = datetime.fromisoformat(
                        published_str.replace("Z", "+00:00")
                    ).replace(tzinfo=None)

            # Abstract URL (the id element is the abstract URL)
            arxiv_url = (entry.findtext(f"{{{ATOM_NS}}}id") or "").strip()

            # Categories
            categories = []
            for cat_el in entry.findall(f"{{{ARXIV_NS}}}primary_category"):
                term = cat_el.get("term")
                if term:
                    categories.append(term)

            entries.append(
                {
                    "title": title,
                    "summary": summary,
                    "author": author_str,
                    "published_at": published_at,
                    "url": arxiv_url,
                    "categories": categories,
                }
            )

        return entries

    def normalize(self, raw_item: dict) -> ContentItemCreate:
        """Convert a raw arXiv entry dict to ContentItemCreate."""
        tags = raw_item.get("categories", [])
        return ContentItemCreate(
            title=raw_item["title"],
            original_url=raw_item["url"],
            content_type="paper",
            source_name=self.source_name,
            summary=raw_item.get("summary"),
            author=raw_item.get("author"),
            published_at=raw_item.get("published_at"),
            topic_tags=tags,
            engagement_score=0,
        )


# Auto-register on import
registry.register(ArxivFetcher())
