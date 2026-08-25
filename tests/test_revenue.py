from __future__ import annotations

import pytest

from creator_seo_mcp.models import (
    CannibalizationGroup,
    DecayResult,
    RevenueConfig,
    StrikingKeyword,
)
from creator_seo_mcp.revenue import score_cannibalization, score_decay, score_striking


@pytest.fixture()
def config():
    return RevenueConfig(site_rpm=20.0, affiliate_categories={"gaming-deals": 2.0})


def test_score_striking_calculates_value(config):
    kw = StrikingKeyword(
        query="best gaming chair",
        page="https://example.com/best-gaming-chair/",
        impressions=5000,
        clicks=100,
        ctr=0.02,
        position=8.0,
        gap_to_page1=5.0,
    )
    result = score_striking(kw, config)
    assert result.est_value > 0
    assert result.type == "striking"
    assert result.query == "best gaming chair"


def test_score_striking_affiliate_multiplier(config):
    kw_regular = StrikingKeyword(
        query="gaming tips",
        page="https://example.com/gaming-tips/",
        impressions=5000,
        clicks=100,
        ctr=0.02,
        position=8.0,
        gap_to_page1=5.0,
    )
    kw_affiliate = StrikingKeyword(
        query="gaming deals",
        page="https://example.com/gaming-deals/best-chair/",
        impressions=5000,
        clicks=100,
        ctr=0.02,
        position=8.0,
        gap_to_page1=5.0,
    )
    regular = score_striking(kw_regular, config)
    affiliate = score_striking(kw_affiliate, config)
    assert affiliate.est_value == pytest.approx(regular.est_value * 2.0)


def test_score_decay_uses_lost_clicks(config):
    decay = DecayResult(
        page="https://example.com/old-post/",
        recent_clicks=400,
        prior_clicks=1000,
        pct_change=-60.0,
        recent_impressions=5000,
        prior_impressions=12000,
    )
    result = score_decay(decay, config)
    assert result.est_traffic_gain == pytest.approx(600.0)
    assert result.est_value > 0
    assert result.type == "decay"


def test_score_cannibalization_returns_nonzero(config):
    group = CannibalizationGroup(
        query="elden ring tips",
        competing_pages=["https://example.com/a/", "https://example.com/b/"],
        primary_page="https://example.com/a/",
        total_impressions=3000,
        note="test",
    )
    result = score_cannibalization(group, config)
    assert result.est_value > 0
    assert result.type == "cannibalization"


def test_score_striking_position1_no_ctr_gain(config):
    kw = StrikingKeyword(
        query="already first",
        page="https://example.com/top/",
        impressions=10000,
        clicks=2790,
        ctr=0.279,
        position=1.0,
        gap_to_page1=0.0,
    )
    result = score_striking(kw, config)
    assert result.est_traffic_gain >= 0


def test_score_striking_larger_gap_scores_higher(config):
    """A keyword with a bigger real gap_to_page1 must score at least as high as one
    closer to page 1, at equal impressions. Scoring should track the tool's own
    striking-distance definition, not shrink as the true opportunity grows."""
    near_page1 = StrikingKeyword(
        query="near", page="https://example.com/near/",
        impressions=1000, clicks=20, ctr=0.02, position=4.0, gap_to_page1=1.0,
    )
    deep_striking = StrikingKeyword(
        query="deep", page="https://example.com/deep/",
        impressions=1000, clicks=20, ctr=0.02, position=15.0, gap_to_page1=12.0,
    )
    result_near = score_striking(near_page1, config)
    result_deep = score_striking(deep_striking, config)
    assert result_deep.est_value >= result_near.est_value
