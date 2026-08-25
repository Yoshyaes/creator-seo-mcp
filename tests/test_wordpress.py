from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from creator_seo_mcp.wordpress import push_wordpress_draft

_POST_RESPONSE = {
    "id": 42,
    "slug": "elden-ring-guide",
    "title": {"rendered": "Elden Ring Guide"},
    "content": {"rendered": "<p>updated</p>"},
    "status": "draft",
    "link": "https://example.com/elden-ring-guide/",
}


def _mock_response(json_body, status: int = 200):
    mock = MagicMock()
    mock.json.return_value = json_body
    mock.status_code = status
    mock.raise_for_status = MagicMock()
    return mock


@patch("creator_seo_mcp.wordpress.httpx.post")
@patch("creator_seo_mcp.wordpress.httpx.get")
def test_push_draft_refuses_to_touch_published_post(mock_get, mock_post, monkeypatch):
    """A post already live must never be silently flipped to draft."""
    monkeypatch.setenv("WORDPRESS_DRAFT_PUSH_ENABLED", "true")
    monkeypatch.setenv("WORDPRESS_USERNAME", "fred")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "app-pass")

    mock_get.return_value = _mock_response({**_POST_RESPONSE, "status": "publish"})

    with pytest.raises(PermissionError, match="already published"):
        push_wordpress_draft("https://example.com", 42, "<p>new content</p>")

    mock_post.assert_not_called()


@patch("creator_seo_mcp.wordpress.httpx.post")
@patch("creator_seo_mcp.wordpress.httpx.get")
def test_push_draft_updates_existing_draft_post(mock_get, mock_post, monkeypatch):
    monkeypatch.setenv("WORDPRESS_DRAFT_PUSH_ENABLED", "true")
    monkeypatch.setenv("WORDPRESS_USERNAME", "fred")
    monkeypatch.setenv("WORDPRESS_APP_PASSWORD", "app-pass")

    mock_get.return_value = _mock_response({**_POST_RESPONSE, "status": "draft"})
    mock_post.return_value = _mock_response(_POST_RESPONSE)

    result = push_wordpress_draft("https://example.com", 42, "<p>new content</p>")

    assert result.status == "draft"
    mock_post.assert_called_once()


def test_push_draft_disabled_by_default(monkeypatch):
    monkeypatch.delenv("WORDPRESS_DRAFT_PUSH_ENABLED", raising=False)

    with pytest.raises(PermissionError, match="disabled"):
        push_wordpress_draft("https://example.com", 42, "<p>new content</p>")
