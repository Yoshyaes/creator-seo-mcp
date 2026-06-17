from __future__ import annotations

from collections import defaultdict

from .gsc import date_range_for, get_service, paginate_search_analytics
from .models import CannibalizationGroup


def find_cannibalization(
    site_url: str,
    days: int = 28,
    min_impressions: int = 30,
) -> list[CannibalizationGroup]:
    service = get_service()
    start_date, end_date = date_range_for(days)

    rows = paginate_search_analytics(
        service,
        site_url,
        start_date,
        end_date,
        dimensions=["query", "page"],
    )

    query_map: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        keys: list[str] = row.get("keys", [])
        query = keys[0] if len(keys) > 0 else ""
        page = keys[1] if len(keys) > 1 else ""
        query_map[query].append(
            {
                "page": page,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
            }
        )

    results: list[CannibalizationGroup] = []
    for query, pages in query_map.items():
        if len(pages) < 2:
            continue
        total_impressions = sum(int(p["impressions"]) for p in pages)
        if total_impressions < min_impressions:
            continue

        pages_sorted = sorted(pages, key=lambda p: int(p["clicks"]), reverse=True)
        primary = str(pages_sorted[0]["page"])
        competing = [str(p["page"]) for p in pages_sorted]

        results.append(
            CannibalizationGroup(
                query=query,
                competing_pages=competing,
                primary_page=primary,
                total_impressions=total_impressions,
                note=f"{len(competing)} pages competing for this query. Consolidate or differentiate.",
            )
        )

    results.sort(key=lambda r: r.total_impressions, reverse=True)
    return results
