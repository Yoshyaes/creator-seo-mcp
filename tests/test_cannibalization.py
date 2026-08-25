from __future__ import annotations

from unittest.mock import MagicMock, patch

from creator_seo_mcp.cannibalization import find_cannibalization


def _mock_service(rows):
    svc = MagicMock()
    svc.searchanalytics().query().execute.return_value = {"rows": rows}
    return svc


@patch("creator_seo_mcp.cannibalization.get_service")
def test_cannibalization_detects_real_competing_pages(mock_get_service):
    rows = [
        {"keys": ["elden ring tips", "https://example.com/a/"], "clicks": 20, "impressions": 500},
        {"keys": ["elden ring tips", "https://example.com/b/"], "clicks": 10, "impressions": 300},
    ]
    mock_get_service.return_value = _mock_service(rows)

    results = find_cannibalization("https://example.com/", min_impressions=30)

    assert len(results) == 1
    assert set(results[0].competing_pages) == {"https://example.com/a/", "https://example.com/b/"}
    assert results[0].primary_page == "https://example.com/a/"


@patch("creator_seo_mcp.cannibalization.get_service")
def test_cannibalization_ignores_fragment_variants_of_same_page(mock_get_service):
    """A table-of-contents jump link (#section) is the same document as its parent
    page, not a competing page, so it must not be reported as self-cannibalization."""
    rows = [
        {"keys": ["backloggd", "https://example.com/review/"], "clicks": 4, "impressions": 11000},
        {"keys": ["backloggd", "https://example.com/review/#intro"], "clicks": 0, "impressions": 50},
        {"keys": ["backloggd", "https://example.com/review/#pricing"], "clicks": 0, "impressions": 20},
    ]
    mock_get_service.return_value = _mock_service(rows)

    results = find_cannibalization("https://example.com/", min_impressions=30)

    assert results == []


@patch("creator_seo_mcp.cannibalization.get_service")
def test_cannibalization_merges_fragment_impressions_into_real_competing_page(mock_get_service):
    """Fragment rows still count toward the real page's totals once merged, and a
    genuinely different page competing for the same query is still detected."""
    rows = [
        {"keys": ["backloggd", "https://example.com/review/"], "clicks": 4, "impressions": 11000},
        {"keys": ["backloggd", "https://example.com/review/#intro"], "clicks": 0, "impressions": 50},
        {"keys": ["backloggd", "https://example.com/comparison/"], "clicks": 2, "impressions": 3000},
    ]
    mock_get_service.return_value = _mock_service(rows)

    results = find_cannibalization("https://example.com/", min_impressions=30)

    assert len(results) == 1
    assert set(results[0].competing_pages) == {"https://example.com/review/", "https://example.com/comparison/"}
    assert results[0].total_impressions == 14050


@patch("creator_seo_mcp.cannibalization.get_service")
def test_cannibalization_excludes_below_impression_floor(mock_get_service):
    rows = [
        {"keys": ["niche query", "https://example.com/a/"], "clicks": 1, "impressions": 5},
        {"keys": ["niche query", "https://example.com/b/"], "clicks": 1, "impressions": 5},
    ]
    mock_get_service.return_value = _mock_service(rows)

    results = find_cannibalization("https://example.com/", min_impressions=30)
    assert results == []
