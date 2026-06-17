from __future__ import annotations

from datetime import date, timedelta

from .gsc import get_service, paginate_search_analytics
from .models import DecayResult


def _period(end: date, days: int) -> tuple[str, str]:
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def analyze_content_decay(
    site_url: str,
    recent_days: int = 28,
    compare_days: int = 28,
    min_clicks: int = 10,
) -> list[DecayResult]:
    service = get_service()
    today = date.today() - timedelta(days=3)

    recent_end = today
    recent_start_str, recent_end_str = _period(recent_end, recent_days)

    prior_end = date.fromisoformat(recent_start_str) - timedelta(days=1)
    prior_start_str, prior_end_str = _period(prior_end, compare_days)

    recent_rows = paginate_search_analytics(
        service, site_url, recent_start_str, recent_end_str, dimensions=["page"]
    )
    prior_rows = paginate_search_analytics(
        service, site_url, prior_start_str, prior_end_str, dimensions=["page"]
    )

    recent_map: dict[str, dict[str, int]] = {}
    for row in recent_rows:
        page = row.get("keys", [""])[0]
        recent_map[page] = {
            "clicks": row.get("clicks", 0),
            "impressions": row.get("impressions", 0),
        }

    prior_map: dict[str, dict[str, int]] = {}
    for row in prior_rows:
        page = row.get("keys", [""])[0]
        prior_map[page] = {
            "clicks": row.get("clicks", 0),
            "impressions": row.get("impressions", 0),
        }

    results: list[DecayResult] = []
    for page, recent in recent_map.items():
        if page not in prior_map:
            continue
        prior = prior_map[page]
        if recent["clicks"] < min_clicks:
            continue
        if prior["clicks"] == 0:
            continue

        pct_change = (recent["clicks"] - prior["clicks"]) / prior["clicks"] * 100.0
        results.append(
            DecayResult(
                page=page,
                recent_clicks=recent["clicks"],
                prior_clicks=prior["clicks"],
                pct_change=pct_change,
                recent_impressions=recent["impressions"],
                prior_impressions=prior["impressions"],
            )
        )

    results.sort(key=lambda r: r.pct_change)
    return results
