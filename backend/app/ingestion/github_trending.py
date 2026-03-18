"""GitHub Trending fetcher - fetches trending AI/ML repos via GitHub Search API."""

import contextlib
from datetime import datetime, timedelta

import httpx

from app.ingestion.base import BaseFetcher, ContentItemCreate
from app.ingestion.registry import registry

# Topics to search for
TOPICS = ["machine-learning", "deep-learning", "artificial-intelligence", "llm", "nlp"]
MAX_RESULTS = 30


class GitHubTrendingFetcher(BaseFetcher):
    """Fetches trending AI/ML repositories from the GitHub Search API."""

    source_name = "GitHub Trending"

    def __init__(self, max_results: int = MAX_RESULTS):
        self.max_results = max_results
        self.api_url = "https://api.github.com/search/repositories"

    async def fetch_raw(self) -> list[dict]:
        """Fetch trending repos from GitHub Search API."""
        # Look for repos created or pushed to in the last 7 days
        since = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        topic_query = " OR ".join(f"topic:{t}" for t in TOPICS)
        query = f"({topic_query}) pushed:>{since}"

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Add token if configured
        from app.config import settings

        if settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                self.api_url,
                params={
                    "q": query,
                    "sort": "stars",
                    "order": "desc",
                    "per_page": str(self.max_results),
                },
                headers=headers,
            )
            resp.raise_for_status()

        data = resp.json()
        return data.get("items", [])

    def normalize(self, raw_item: dict) -> ContentItemCreate:
        """Convert a GitHub repo JSON to ContentItemCreate."""
        title = raw_item.get("full_name", "")
        description = raw_item.get("description") or ""

        # Truncate description
        if len(description) > 500:
            description = description[:497] + "..."

        # Published at: use pushed_at (most recent activity)
        published_at = None
        pushed_str = raw_item.get("pushed_at") or raw_item.get("created_at")
        if pushed_str:
            with contextlib.suppress(ValueError):
                published_at = datetime.fromisoformat(pushed_str.replace("Z", "+00:00")).replace(
                    tzinfo=None
                )

        owner = raw_item.get("owner", {}).get("login", "")
        topics = raw_item.get("topics", [])[:10]  # cap tags
        stars = raw_item.get("stargazers_count", 0)

        return ContentItemCreate(
            title=title,
            original_url=raw_item.get("html_url", ""),
            content_type="repo",
            source_name=self.source_name,
            summary=description,
            author=owner,
            published_at=published_at,
            topic_tags=topics,
            engagement_score=stars,
        )


# Auto-register on import
registry.register(GitHubTrendingFetcher())
