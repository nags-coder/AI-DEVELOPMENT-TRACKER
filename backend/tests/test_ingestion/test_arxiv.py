"""Tests for the ArXiv fetcher."""

from pathlib import Path

from app.ingestion.arxiv import ArxivFetcher

FIXTURES = Path(__file__).parent / "fixtures"


class TestArxivParsing:
    def setup_method(self):
        self.fetcher = ArxivFetcher()
        self.xml_text = (FIXTURES / "arxiv_response.xml").read_text()

    def test_parse_atom_returns_entries(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        assert len(entries) == 2

    def test_parse_atom_extracts_title(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        assert entries[0]["title"] == "Test Paper: Attention Is Still All You Need"

    def test_parse_atom_extracts_summary(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        assert "transformer architecture" in entries[0]["summary"]

    def test_parse_atom_extracts_authors(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        # First entry has 4 authors; we take first 3 + "et al."
        assert "Alice Smith" in entries[0]["author"]
        assert "et al." in entries[0]["author"]

    def test_parse_atom_extracts_url(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        assert entries[0]["url"] == "http://arxiv.org/abs/2403.12345v1"

    def test_parse_atom_extracts_published_at(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        assert entries[0]["published_at"] is not None
        assert entries[0]["published_at"].year == 2025

    def test_parse_atom_extracts_categories(self):
        entries = self.fetcher._parse_atom(self.xml_text)
        assert "cs.AI" in entries[0]["categories"]


class TestArxivNormalization:
    def setup_method(self):
        self.fetcher = ArxivFetcher()

    def test_normalize_produces_content_item_create(self):
        raw = {
            "title": "Test",
            "url": "http://arxiv.org/abs/9999",
            "summary": "A summary",
            "author": "Test Author",
            "published_at": None,
            "categories": ["cs.AI"],
        }
        item = self.fetcher.normalize(raw)
        assert item.title == "Test"
        assert item.original_url == "http://arxiv.org/abs/9999"
        assert item.content_type == "paper"
        assert item.source_name == "arXiv"
        assert item.topic_tags == ["cs.AI"]
