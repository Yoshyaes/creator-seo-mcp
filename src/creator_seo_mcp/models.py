from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    status: str
    version: str
    verified_sites: list[str] = Field(default_factory=list)


class QueryRow(BaseModel):
    query: str
    clicks: int
    impressions: int
    ctr: float
    position: float


class StrikingKeyword(BaseModel):
    query: str
    page: str
    impressions: int
    clicks: int
    ctr: float
    position: float
    gap_to_page1: float


class PagePerformance(BaseModel):
    page: str
    clicks: int
    impressions: int
    ctr: float
    position: float
    top_queries: list[QueryRow]


class DecayResult(BaseModel):
    page: str
    recent_clicks: int
    prior_clicks: int
    pct_change: float
    recent_impressions: int
    prior_impressions: int


class OnPageAudit(BaseModel):
    url: str
    title: str
    meta_description: str
    h1: str
    headings: list[str]
    word_count: int
    target_in_title: bool
    target_in_h1: bool
    target_density: float
    suggestions: list[str]


class CannibalizationGroup(BaseModel):
    query: str
    competing_pages: list[str]
    primary_page: str
    total_impressions: int
    note: str


class Opportunity(BaseModel):
    type: Literal["striking", "decay", "cannibalization"]
    page: str
    query: str | None
    est_traffic_gain: float
    est_value: float
    score: float
    recommended_action: str


class RevenueConfig(BaseModel):
    site_rpm: float = Field(default=15.0, description="Display ad RPM in USD")
    affiliate_categories: dict[str, float] = Field(
        default_factory=dict,
        description="URL path prefix to commission multiplier mapping",
    )
    ctr_curve: dict[int, float] = Field(
        default_factory=lambda: {
            1: 0.279,
            2: 0.153,
            3: 0.105,
            4: 0.071,
            5: 0.051,
            6: 0.040,
            7: 0.031,
            8: 0.026,
            9: 0.022,
            10: 0.019,
            11: 0.017,
            12: 0.015,
            13: 0.014,
            14: 0.013,
            15: 0.012,
        },
        description="Expected CTR by position (Advanced Web Ranking averages). Override via CREATOR_SEO_CTR_CURVE env var.",  # noqa: E501
    )
