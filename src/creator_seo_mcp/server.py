from __future__ import annotations

import asyncio
import os
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from . import __version__
from .cannibalization import find_cannibalization as _find_cannibalization
from .config import load_revenue_config, token_path
from .decay import analyze_content_decay as _analyze_content_decay
from .gsc import SCOPES, list_verified_sites as _list_verified_sites
from .models import (
    CannibalizationGroup,
    DecayResult,
    HealthCheck,
    OnPageAudit,
    Opportunity,
    PagePerformance,
    RevenueConfig,
    StrikingKeyword,
)
from .onpage import audit_page_onpage as _audit_page_onpage
from .revenue import score_cannibalization, score_decay, score_striking
from .striking import get_striking_distance_keywords as _get_striking_distance_keywords

mcp = FastMCP(
    name="creator-seo-mcp",
    instructions=(
        "Revenue-weighted SEO assistant for content creators. "
        "Connects to Google Search Console and reads page content to rank SEO opportunities by estimated revenue."
    ),
)


@mcp.tool()
def health_check() -> HealthCheck:
    """Check that the server is running and list your verified GSC properties."""
    from google.oauth2.credentials import Credentials

    try:
        sites = _list_verified_sites()
    except Exception:
        sites = []

    token = token_path()
    token_status = "missing"
    if os.path.exists(token):
        try:
            creds = Credentials.from_authorized_user_file(token, SCOPES)  # type: ignore[no-untyped-call]
            if creds.valid:
                token_status = "valid"
            elif creds.expired:
                token_status = "expired"
            else:
                token_status = "invalid"
        except Exception:
            token_status = "unreadable"

    return HealthCheck(status="ok", version=__version__, verified_sites=sites, token_status=token_status)


@mcp.tool()
def list_sites() -> list[str]:
    """List all Google Search Console properties you have access to."""
    return _list_verified_sites()


@mcp.tool()
def get_striking_distance_keywords(
    site_url: Annotated[str, Field(description="GSC property URL, e.g. https://example.com/")],
    days: Annotated[int, Field(description="Lookback window in days", ge=7, le=90)] = 28,
    min_impressions: Annotated[int, Field(description="Minimum impressions to include", ge=1)] = 50,
    position_min: Annotated[float, Field(description="Minimum average position", ge=1.0)] = 4.0,
    position_max: Annotated[float, Field(description="Maximum average position", le=100.0)] = 15.0,
    limit: Annotated[int, Field(description="Max results to return", ge=1, le=500)] = 50,
) -> list[StrikingKeyword]:
    """
    Find queries ranking in striking distance of page 1 (positions 4-15 by default).
    Results are sorted by impression volume so the highest-potential opportunities come first.
    """
    return _get_striking_distance_keywords(
        site_url=site_url,
        days=days,
        min_impressions=min_impressions,
        position_min=position_min,
        position_max=position_max,
        limit=limit,
    )


@mcp.tool()
def get_page_performance(
    site_url: Annotated[str, Field(description="GSC property URL")],
    page_url: Annotated[str, Field(description="Full URL of the page to analyze")],
    days: Annotated[int, Field(description="Lookback window in days", ge=7, le=90)] = 28,
) -> PagePerformance:
    """Full GSC picture for one URL: clicks, impressions, CTR, position, and top queries."""
    from .gsc import date_range_for, get_service, paginate_search_analytics

    service = get_service()
    start_date, end_date = date_range_for(days)

    filters = [{"dimension": "page", "operator": "equals", "expression": page_url}]
    rows = paginate_search_analytics(
        service, site_url, start_date, end_date, dimensions=["query"], filters=filters
    )

    total_clicks = sum(r.get("clicks", 0) for r in rows)
    total_impressions = sum(r.get("impressions", 0) for r in rows)
    positions = [r.get("position", 0.0) * r.get("impressions", 0) for r in rows]
    avg_position = (
        sum(positions) / total_impressions if total_impressions > 0 else 0.0
    )
    avg_ctr = total_clicks / total_impressions if total_impressions > 0 else 0.0

    from .models import QueryRow

    top_queries = sorted(rows, key=lambda r: r.get("clicks", 0), reverse=True)[:10]
    query_rows = [
        QueryRow(
            query=r.get("keys", [""])[0],
            clicks=r.get("clicks", 0),
            impressions=r.get("impressions", 0),
            ctr=r.get("ctr", 0.0),
            position=r.get("position", 0.0),
        )
        for r in top_queries
    ]

    return PagePerformance(
        page=page_url,
        clicks=total_clicks,
        impressions=total_impressions,
        ctr=round(avg_ctr, 4),
        position=round(avg_position, 2),
        top_queries=query_rows,
    )


@mcp.tool()
def analyze_content_decay(
    site_url: Annotated[str, Field(description="GSC property URL")],
    recent_days: Annotated[int, Field(description="Length of the recent period in days", ge=7, le=90)] = 28,
    compare_days: Annotated[int, Field(description="Length of the comparison period in days", ge=7, le=90)] = 28,
    min_clicks: Annotated[int, Field(description="Minimum clicks in recent period to include", ge=1)] = 10,
) -> list[DecayResult]:
    """
    Compare recent vs prior period for every page and flag declining traffic.
    Results are sorted worst decliners first (most negative percent change at top).
    """
    return _analyze_content_decay(
        site_url=site_url,
        recent_days=recent_days,
        compare_days=compare_days,
        min_clicks=min_clicks,
    )


@mcp.tool()
def audit_page_onpage(
    page_url: Annotated[str, Field(description="Full URL of the page to audit")],
    target_query: Annotated[str, Field(description="The search query you want this page to rank for")],
) -> OnPageAudit:
    """
    Fetch a page, parse its title/meta/headings/body, and return concrete edit suggestions
    for the target query.
    """
    return _audit_page_onpage(page_url=page_url, target_query=target_query)


@mcp.tool()
def find_cannibalization(
    site_url: Annotated[str, Field(description="GSC property URL")],
    days: Annotated[int, Field(description="Lookback window in days", ge=7, le=90)] = 28,
    min_impressions: Annotated[int, Field(description="Minimum total impressions across competing pages", ge=1)] = 30,
) -> list[CannibalizationGroup]:
    """
    Find queries where multiple pages are competing, splitting authority and confusing Google.
    Results are sorted by total impression volume.
    """
    return _find_cannibalization(
        site_url=site_url,
        days=days,
        min_impressions=min_impressions,
    )


@mcp.tool()
def get_top_opportunities(
    site_url: Annotated[str, Field(description="GSC property URL")],
    days: Annotated[int, Field(description="Lookback window in days", ge=7, le=90)] = 28,
    limit: Annotated[int, Field(description="Max opportunities to return", ge=1, le=100)] = 20,
    site_rpm: Annotated[float | None, Field(description="Override display ad RPM in USD (default from env)")] = None,
) -> list[Opportunity]:
    """
    The headline call. Combines striking-distance keywords, content decay, and cannibalization,
    weights each by estimated revenue, and returns a single ranked action list.
    Revenue estimates use your configured RPM and affiliate multipliers.
    """
    revenue_config = load_revenue_config(
        RevenueConfig(site_rpm=site_rpm) if site_rpm is not None else None
    )

    striking, decay, cannibalization = asyncio.run(
        _gather_all(site_url, days)
    )

    opportunities: list[Opportunity] = []
    for kw in striking:
        opportunities.append(score_striking(kw, revenue_config))
    for d in decay:
        opportunities.append(score_decay(d, revenue_config))
    for c in cannibalization:
        opportunities.append(score_cannibalization(c, revenue_config))

    opportunities.sort(key=lambda o: o.score, reverse=True)
    return opportunities[:limit]


async def _gather_all(
    site_url: str, days: int
) -> tuple[list[StrikingKeyword], list[DecayResult], list[CannibalizationGroup]]:
    loop = asyncio.get_event_loop()
    striking, decay, cannibalization = await asyncio.gather(
        loop.run_in_executor(None, _get_striking_distance_keywords, site_url, days),
        loop.run_in_executor(None, _analyze_content_decay, site_url, days),
        loop.run_in_executor(None, _find_cannibalization, site_url, days),
    )
    return striking, decay, cannibalization


def main() -> None:
    mcp.run()
