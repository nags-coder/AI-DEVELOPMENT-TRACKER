"""Tests for the scoring/ranker module."""

from datetime import datetime, timedelta

from app.scoring.ranker import (
    engagement_normalized,
    quality_score,
    recency_score,
    type_boost,
)


class TestRecencyScore:
    def test_today_is_max(self):
        now = datetime.now()
        score = recency_score(now, now)
        assert score == 1.0

    def test_half_life_decay(self):
        """Score roughly halves every RECENCY_HALF_LIFE (3) days."""
        now = datetime.now()
        three_days_ago = now - timedelta(days=3)
        score = recency_score(three_days_ago, now)
        assert 0.45 <= score <= 0.55  # should be ~0.5

    def test_seven_days_ago_is_low(self):
        now = datetime.now()
        seven_days = now - timedelta(days=7)
        score = recency_score(seven_days, now)
        assert score < 0.25

    def test_thirty_plus_days_is_zero(self):
        now = datetime.now()
        old = now - timedelta(days=31)
        score = recency_score(old, now)
        assert score == 0.0

    def test_none_published_at_returns_zero(self):
        score = recency_score(None)
        assert score == 0.0


class TestQualityScore:
    def test_rating_5_is_max(self):
        assert quality_score(5) == 1.0

    def test_rating_1_is_low(self):
        assert quality_score(1) == 0.2

    def test_none_rating_defaults_to_3(self):
        assert quality_score(None) == 0.6


class TestEngagementNormalized:
    def test_zero_engagement(self):
        assert engagement_normalized(0) == 0.0

    def test_at_cap(self):
        assert engagement_normalized(10000) == 1.0

    def test_above_cap_clipped(self):
        assert engagement_normalized(50000) == 1.0

    def test_half_cap(self):
        assert engagement_normalized(5000) == 0.5


class TestTypeBoost:
    def test_paper_is_high(self):
        assert type_boost("paper") == 0.8

    def test_repo(self):
        assert type_boost("repo") == 0.7

    def test_unknown_type_gets_default(self):
        assert type_boost("unknown_type") == 0.5


class TestScoreRange:
    """Score output should always be in [0.0, 1.0]."""

    def test_score_range_for_various_inputs(self):
        from unittest.mock import MagicMock

        from app.scoring.ranker import score_item

        now = datetime.now()
        cases = [
            # (engagement, user_rating, published_at, content_type)
            (0, None, now, "paper"),
            (50000, 5, now, "repo"),
            (0, 1, now - timedelta(days=30), "blog"),
            (100, 3, now - timedelta(hours=6), "model"),
        ]

        for eng, rating, pub, ctype in cases:
            item = MagicMock()
            item.published_at = pub
            item.engagement_score = eng
            item.content_type = ctype

            source = MagicMock()
            source.user_rating = rating

            score = score_item(item, source, now)
            assert 0.0 <= score <= 1.0, f"Score {score} out of range for {ctype}"

    def test_higher_rated_source_scores_higher(self):
        from unittest.mock import MagicMock

        from app.scoring.ranker import score_item

        now = datetime.now()

        item = MagicMock()
        item.published_at = now
        item.engagement_score = 100
        item.content_type = "paper"

        source_low = MagicMock()
        source_low.user_rating = 1

        source_high = MagicMock()
        source_high.user_rating = 5

        score_low = score_item(item, source_low, now)
        score_high = score_item(item, source_high, now)
        assert score_high > score_low
