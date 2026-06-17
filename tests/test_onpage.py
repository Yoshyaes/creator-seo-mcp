from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from creator_seo_mcp.onpage import audit_page_onpage

_GOOD_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Best Elden Ring Starting Class for Beginners</title>
  <meta name="description" content="Find the perfect Elden Ring starting class with our in-depth guide.">
</head>
<body>
  <nav><a href="/">Home</a></nav>
  <article>
    <h1>Best Elden Ring Starting Class for Beginners</h1>
    <h2>What is the Best Starting Class?</h2>
    <h2>Vagabond Build</h2>
    <h3>Stats Overview</h3>
    <p>The best elden ring starting class for beginners is the Vagabond.
    Choosing the right elden ring starting class matters a lot.</p>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. """ + " word " * 1500 + """</p>
  </article>
  <footer>Footer</footer>
</body>
</html>
"""

_MINIMAL_HTML = """
<html><head><title>Short</title></head>
<body><p>Just a few words.</p></body>
</html>
"""

_NO_H1_HTML = """
<html><head><title>Page Without H1</title></head>
<body><article><p>Content without an H1 tag. """ + " text " * 200 + """</p></article></body>
</html>
"""


def _mock_response(html: str, status: int = 200):
    mock = MagicMock()
    mock.text = html
    mock.status_code = status
    mock.raise_for_status = MagicMock()
    return mock


@patch("creator_seo_mcp.onpage.httpx.get")
def test_audit_good_page(mock_get):
    mock_get.return_value = _mock_response(_GOOD_HTML)
    result = audit_page_onpage("https://example.com/elden-ring/", "elden ring starting class")

    assert result.target_in_title is True
    assert result.target_in_h1 is True
    assert result.word_count > 100
    assert isinstance(result.suggestions, list)


@patch("creator_seo_mcp.onpage.httpx.get")
def test_audit_minimal_page_has_suggestions(mock_get):
    mock_get.return_value = _mock_response(_MINIMAL_HTML)
    result = audit_page_onpage("https://example.com/short/", "gaming tips")

    assert result.target_in_title is False
    assert result.target_in_h1 is False
    assert any("title" in s.lower() for s in result.suggestions)
    assert any("H1" in s for s in result.suggestions)
    assert result.word_count < 1500


@patch("creator_seo_mcp.onpage.httpx.get")
def test_audit_no_h1(mock_get):
    mock_get.return_value = _mock_response(_NO_H1_HTML)
    result = audit_page_onpage("https://example.com/no-h1/", "some query")

    assert result.h1 == ""
    assert any("H1" in s for s in result.suggestions)


@patch("creator_seo_mcp.onpage.httpx.get")
def test_audit_raises_on_http_error(mock_get):
    import httpx

    mock_get.side_effect = httpx.HTTPError("Connection refused")

    with pytest.raises(RuntimeError, match="Failed to fetch"):
        audit_page_onpage("https://example.com/broken/", "query")
