from __future__ import annotations

from unittest.mock import MagicMock, patch

from conftest import load_fixture

from creator_seo_mcp.decay import analyze_content_decay


def _mock_service_sequential(recent_rows, prior_rows):
    """Return a service mock whose execute() alternates between two result sets."""
    svc = MagicMock()
    svc.searchanalytics().query().execute.side_effect = [
        {"rows": recent_rows},
        {"rows": prior_rows},
    ]
    return svc


@patch("creator_seo_mcp.decay.get_service")
def test_decay_detects_declining_pages(mock_get_service):
    recent = load_fixture("decay_recent.json")
    prior = load_fixture("decay_prior.json")
    mock_get_service.return_value = _mock_service_sequential(recent, prior)

    results = analyze_content_decay("https://example.com/", min_clicks=10)

    assert len(results) >= 1
    worst = results[0]
    assert worst.pct_change < 0


@patch("creator_seo_mcp.decay.get_service")
def test_decay_sorted_worst_first(mock_get_service):
    recent = load_fixture("decay_recent.json")
    prior = load_fixture("decay_prior.json")
    mock_get_service.return_value = _mock_service_sequential(recent, prior)

    results = analyze_content_decay("https://example.com/", min_clicks=10)

    for i in range(len(results) - 1):
        assert results[i].pct_change <= results[i + 1].pct_change


@patch("creator_seo_mcp.decay.get_service")
def test_decay_empty_recent(mock_get_service):
    mock_get_service.return_value = _mock_service_sequential([], [])
    results = analyze_content_decay("https://example.com/")
    assert results == []


@patch("creator_seo_mcp.decay.get_service")
def test_decay_excludes_pure_noise(mock_get_service):
    """Pages that never had meaningful traffic in either period are noise, not decay."""
    recent = [{"keys": ["https://example.com/low/"], "clicks": 3, "impressions": 100}]
    prior = [{"keys": ["https://example.com/low/"], "clicks": 5, "impressions": 150}]
    mock_get_service.return_value = _mock_service_sequential(recent, prior)

    results = analyze_content_decay("https://example.com/", min_clicks=10)
    assert results == []


@patch("creator_seo_mcp.decay.get_service")
def test_decay_flags_pages_that_collapsed_to_near_zero(mock_get_service):
    """A page that fell from 200 clicks to 3 is the worst kind of decay and must be flagged,
    even though its recent click count alone is below min_clicks."""
    recent = [{"keys": ["https://example.com/collapsed/"], "clicks": 3, "impressions": 100}]
    prior = [{"keys": ["https://example.com/collapsed/"], "clicks": 200, "impressions": 5000}]
    mock_get_service.return_value = _mock_service_sequential(recent, prior)

    results = analyze_content_decay("https://example.com/", min_clicks=10)
    assert len(results) == 1
    assert results[0].page == "https://example.com/collapsed/"
    assert results[0].pct_change < -95
