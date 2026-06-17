from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from conftest import load_fixture

from creator_seo_mcp.striking import get_striking_distance_keywords


def _mock_service(rows):
    svc = MagicMock()
    svc.searchanalytics().query().execute.return_value = {"rows": rows}
    return svc


@patch("creator_seo_mcp.striking.get_service")
@patch("creator_seo_mcp.striking.date_range_for", return_value=("2025-01-01", "2025-01-28"))
def test_striking_returns_filtered_results(mock_date, mock_get_service):
    rows = load_fixture("striking_sample.json")
    mock_get_service.return_value = _mock_service(rows)

    results = get_striking_distance_keywords("https://example.com/", min_impressions=50)

    assert len(results) == 3
    for r in results:
        assert 4.0 <= r.position <= 15.0
        assert r.impressions >= 50

    assert results[0].impressions >= results[-1].impressions


@patch("creator_seo_mcp.striking.get_service")
@patch("creator_seo_mcp.striking.date_range_for", return_value=("2025-01-01", "2025-01-28"))
def test_striking_empty_results(mock_date, mock_get_service):
    mock_get_service.return_value = _mock_service([])
    results = get_striking_distance_keywords("https://example.com/")
    assert results == []


@patch("creator_seo_mcp.striking.get_service")
@patch("creator_seo_mcp.striking.date_range_for", return_value=("2025-01-01", "2025-01-28"))
def test_striking_respects_limit(mock_date, mock_get_service):
    rows = load_fixture("striking_sample.json")
    mock_get_service.return_value = _mock_service(rows)

    results = get_striking_distance_keywords("https://example.com/", limit=2)
    assert len(results) <= 2


@patch("creator_seo_mcp.striking.paginate_search_analytics")
@patch("creator_seo_mcp.striking.get_service")
@patch("creator_seo_mcp.striking.date_range_for", return_value=("2025-01-01", "2025-01-28"))
def test_striking_pagination_called(mock_date, mock_get_service, mock_paginate):
    mock_paginate.return_value = []
    get_striking_distance_keywords("https://example.com/")
    mock_paginate.assert_called_once()


@patch("creator_seo_mcp.striking.get_service")
@patch("creator_seo_mcp.striking.date_range_for", return_value=("2025-01-01", "2025-01-28"))
def test_gap_to_page1_calculated(mock_date, mock_get_service):
    rows = [
        {"keys": ["test query", "https://example.com/page/"],
         "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 8.0}
    ]
    mock_get_service.return_value = _mock_service(rows)

    results = get_striking_distance_keywords("https://example.com/")
    assert results[0].gap_to_page1 == pytest.approx(5.0)
