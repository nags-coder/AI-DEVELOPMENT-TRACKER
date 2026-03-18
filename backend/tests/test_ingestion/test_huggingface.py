"""Tests for the Hugging Face fetcher."""

import json
from pathlib import Path

from app.ingestion.huggingface import HuggingFaceFetcher

FIXTURES = Path(__file__).parent / "fixtures"


class TestHuggingFacePaperNormalization:
    def setup_method(self):
        self.fetcher = HuggingFaceFetcher()
        self.papers = json.loads((FIXTURES / "hf_papers.json").read_text())

    def test_normalize_paper_title(self):
        item = self.fetcher.normalize(self.papers[0])
        assert "Scaling Reward Models" in item.title

    def test_normalize_paper_content_type(self):
        item = self.fetcher.normalize(self.papers[0])
        assert item.content_type == "paper"

    def test_normalize_paper_url(self):
        item = self.fetcher.normalize(self.papers[0])
        assert "huggingface.co/papers/2403.99901" in item.original_url

    def test_normalize_paper_authors(self):
        item = self.fetcher.normalize(self.papers[0])
        assert "Test Author A" in item.author

    def test_normalize_paper_engagement(self):
        item = self.fetcher.normalize(self.papers[0])
        assert item.engagement_score == 42

    def test_normalize_paper_tags(self):
        item = self.fetcher.normalize(self.papers[0])
        assert "rlhf" in item.topic_tags


class TestHuggingFaceModelNormalization:
    def setup_method(self):
        self.fetcher = HuggingFaceFetcher()
        self.models = json.loads((FIXTURES / "hf_models.json").read_text())

    def test_normalize_model_title(self):
        item = self.fetcher.normalize(self.models[0])
        assert item.title == "test-org/test-model-7b"

    def test_normalize_model_content_type(self):
        item = self.fetcher.normalize(self.models[0])
        assert item.content_type == "model"

    def test_normalize_model_downloads_as_engagement(self):
        item = self.fetcher.normalize(self.models[0])
        assert item.engagement_score == 150000

    def test_normalize_model_author(self):
        item = self.fetcher.normalize(self.models[0])
        assert item.author == "test-org"

    def test_normalize_model_tags_include_pipeline(self):
        item = self.fetcher.normalize(self.models[0])
        assert "text-generation" in item.topic_tags

    def test_normalize_model_url(self):
        item = self.fetcher.normalize(self.models[0])
        assert item.original_url == "https://huggingface.co/test-org/test-model-7b"

    def test_normalize_model_summary(self):
        item = self.fetcher.normalize(self.models[0])
        assert item.summary == "A test 7B parameter language model."


class TestHuggingFaceMixedContent:
    def test_fetcher_handles_both_types(self):
        fetcher = HuggingFaceFetcher()
        papers = json.loads((FIXTURES / "hf_papers.json").read_text())
        models = json.loads((FIXTURES / "hf_models.json").read_text())

        items = [fetcher.normalize(p) for p in papers] + [fetcher.normalize(m) for m in models]
        types = {i.content_type for i in items}
        assert "paper" in types
        assert "model" in types
