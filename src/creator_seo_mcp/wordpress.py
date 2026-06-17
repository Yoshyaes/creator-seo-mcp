from __future__ import annotations

import os

import httpx
from pydantic import BaseModel


class WordPressPost(BaseModel):
    id: int
    slug: str
    title: str
    content: str
    status: str
    link: str


def _wp_auth() -> tuple[str, str]:
    username = os.environ.get("WORDPRESS_USERNAME", "")
    password = os.environ.get("WORDPRESS_APP_PASSWORD", "")
    if not username or not password:
        raise ValueError(
            "WORDPRESS_USERNAME and WORDPRESS_APP_PASSWORD env vars are required. "
            "Create an Application Password in WordPress under Users > Profile."
        )
    return username, password


def get_post_content(site_url: str, post_id_or_slug: str) -> WordPressPost:
    """Fetch a WordPress post by ID or slug via the REST API."""
    site_url = site_url.rstrip("/")
    auth = _wp_auth()

    try:
        post_id = int(post_id_or_slug)
        url = f"{site_url}/wp-json/wp/v2/posts/{post_id}"
        params: dict[str, str] = {}
    except ValueError:
        url = f"{site_url}/wp-json/wp/v2/posts"
        params = {"slug": post_id_or_slug}

    resp = httpx.get(url, params=params, auth=auth, timeout=10.0)
    resp.raise_for_status()

    data = resp.json()
    if isinstance(data, list):
        if not data:
            raise ValueError(f"No post found with slug: {post_id_or_slug}")
        data = data[0]

    return WordPressPost(
        id=data["id"],
        slug=data["slug"],
        title=data["title"]["rendered"],
        content=data["content"]["rendered"],
        status=data["status"],
        link=data["link"],
    )


def push_wordpress_draft(site_url: str, post_id: int, content: str, title: str | None = None) -> WordPressPost:
    """
    Push an updated draft back to WordPress. Requires WORDPRESS_DRAFT_PUSH_ENABLED=true.
    Never auto-publishes. Sets status to 'draft' always.
    """
    if os.environ.get("WORDPRESS_DRAFT_PUSH_ENABLED", "false").lower() != "true":
        raise PermissionError(
            "WordPress draft push is disabled. "
            "Set WORDPRESS_DRAFT_PUSH_ENABLED=true in your environment to enable it."
        )

    site_url = site_url.rstrip("/")
    auth = _wp_auth()

    body: dict[str, str] = {"content": content, "status": "draft"}
    if title:
        body["title"] = title

    resp = httpx.post(
        f"{site_url}/wp-json/wp/v2/posts/{post_id}",
        json=body,
        auth=auth,
        timeout=15.0,
    )
    resp.raise_for_status()
    data = resp.json()

    return WordPressPost(
        id=data["id"],
        slug=data["slug"],
        title=data["title"]["rendered"],
        content=data["content"]["rendered"],
        status=data["status"],
        link=data["link"],
    )
