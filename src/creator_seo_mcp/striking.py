from __future__ import annotations

from .gsc import date_range_for, get_service, paginate_search_analytics
from .models import StrikingKeyword


def get_striking_distance_keywords(
    site_url: str,
    days: int = 28,
    min_impressions: int = 50,
    position_min: float = 4.0,
    position_max: float = 15.0,
    limit: int = 50,
) -> list[StrikingKeyword]:
    service = get_service()
    start_date, end_date = date_range_for(days)

    rows = paginate_search_analytics(
        service,
        site_url,
        start_date,
        end_date,
        dimensions=["query", "page"],
    )

    results: list[StrikingKeyword] = []
    for row in rows:
        position = row.get("position", 0.0)
        impressions = row.get("impressions", 0)

        if not (position_min <= position <= position_max):
            continue
        if impressions < min_impressions:
            continue

        keys: list[str] = row.get("keys", [])
        query = keys[0] if len(keys) > 0 else ""
        page = keys[1] if len(keys) > 1 else ""

        results.append(
            StrikingKeyword(
                query=query,
                page=page,
                impressions=impressions,
                clicks=row.get("clicks", 0),
                ctr=row.get("ctr", 0.0),
                position=position,
                gap_to_page1=max(0.0, position - 3.0),
            )
        )

    results.sort(key=lambda r: r.impressions, reverse=True)
    return results[:limit]
