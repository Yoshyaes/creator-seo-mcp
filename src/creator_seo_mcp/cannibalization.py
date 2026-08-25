from __future__ import annotations

from collections import defaultdict
from urllib.parse import urldefrag

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

    # Two GSC "page" rows that differ only by URL fragment (e.g. an in-page jump
    # link like #section) are the same document, not competing pages, so fragments
    # are stripped before grouping.
    query_page_map: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"clicks": 0, "impressions": 0})
    )
    for row in rows:
        keys: list[str] = row.get("keys", [])
        query = keys[0] if len(keys) > 0 else ""
        raw_page = keys[1] if len(keys) > 1 else ""
        page, _ = urldefrag(raw_page)

        entry = query_page_map[query][page]
        entry["clicks"] += row.get("clicks", 0)
        entry["impressions"] += row.get("impressions", 0)

    results: list[CannibalizationGroup] = []
    for query, pages in query_page_map.items():
        if len(pages) < 2:
            continue
        total_impressions = sum(p["impressions"] for p in pages.values())
        if total_impressions < min_impressions:
            continue

        pages_sorted = sorted(pages.items(), key=lambda item: item[1]["clicks"], reverse=True)
        primary = pages_sorted[0][0]
        competing = [page for page, _ in pages_sorted]

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
