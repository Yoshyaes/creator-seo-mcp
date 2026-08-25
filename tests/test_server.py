from __future__ import annotations

from unittest.mock import patch

from creator_seo_mcp.server import _gather_all


async def test_gather_all_uses_matching_decay_periods():
    """get_top_opportunities(days=N) must compare an N-day recent period against an
    N-day prior period for decay, not mix N recent days against a fixed 28-day prior."""
    with (
        patch("creator_seo_mcp.server._get_striking_distance_keywords", return_value=[]),
        patch("creator_seo_mcp.server._analyze_content_decay", return_value=[]) as mock_decay,
        patch("creator_seo_mcp.server._find_cannibalization", return_value=[]),
    ):
        await _gather_all("https://example.com/", 90)

    mock_decay.assert_called_once_with("https://example.com/", 90, 90)
