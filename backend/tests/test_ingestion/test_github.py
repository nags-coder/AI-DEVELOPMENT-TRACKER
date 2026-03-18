"""Tests for the GitHub Trending fetcher."""

import json
from pathlib import Path

from app.ingestion.github_trending import GitHubTrendingFetcher

FIXTURES = Path(__file__).parent / "fixtures"


class TestGitHubNormalization:
    def setup_method(self):
        self.fetcher = GitHubTrendingFetcher()
        self.items = json.loads((FIXTURES / "github_trending.json").read_text())

    def test_normalize_extracts_title(self):
        item = self.fetcher.normalize(self.items[0])
        assert item.title == "test-org/ai-framework"

    def test_normalize_extracts_url(self):
        item = self.fetcher.normalize(self.items[0])
        assert item.original_url == "https://github.com/test-org/ai-framework"

    def test_normalize_content_type_is_repo(self):
        item = self.fetcher.normalize(self.items[0])
        assert item.content_type == "repo"

    def test_normalize_extracts_stars_as_engagement(self):
        item = self.fetcher.normalize(self.items[0])
        assert item.engagement_score == 15000

    def test_normalize_extracts_author(self):
        item = self.fetcher.normalize(self.items[0])
        assert item.author == "test-org"

    def test_normalize_extracts_topics(self):
        item = self.fetcher.normalize(self.items[0])
        assert "machine-learning" in item.topic_tags

    def test_normalize_extracts_published_at(self):
        item = self.fetcher.normalize(self.items[0])
        assert item.published_at is not None
        assert item.published_at.year == 2025

    def test_normalize_all_items(self):
        """All fixture items normalize successfully."""
        for raw in self.items:
            item = self.fetcher.normalize(raw)
            assert item.title
            assert item.original_url
