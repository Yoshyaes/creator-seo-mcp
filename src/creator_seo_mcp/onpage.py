from __future__ import annotations

import re

import httpx
from selectolax.parser import HTMLParser

from .models import OnPageAudit

_USER_AGENT = (
    "Mozilla/5.0 (compatible; creator-seo-mcp/0.1; +https://github.com/yoshyaes/creator-seo-mcp)"
)
_STRIP_SELECTORS = [
    "nav", "header", "footer", "aside", ".sidebar", ".menu", ".nav",
    ".footer", ".header", ".advertisement", ".ad", "[class*='widget']",
    "[class*='cookie']", "[id*='cookie']",
]


def _extract_text(parser: HTMLParser, selector: str, default: str = "") -> str:
    node = parser.css_first(selector)
    if node is None:
        return default
    return (node.text(strip=True) or default).strip()


def _strip_boilerplate(parser: HTMLParser) -> None:
    for sel in _STRIP_SELECTORS:
        for node in parser.css(sel):
            node.decompose()


def audit_page_onpage(page_url: str, target_query: str) -> OnPageAudit:
    try:
        resp = httpx.get(
            page_url,
            follow_redirects=True,
            timeout=10.0,
            headers={"User-Agent": _USER_AGENT},
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to fetch {page_url}: {e}") from e

    parser = HTMLParser(resp.text)

    title = _extract_text(parser, "title")
    meta_desc = ""
    meta_node = parser.css_first('meta[name="description"]')
    if meta_node:
        meta_desc = meta_node.attributes.get("content", "") or ""

    h1 = _extract_text(parser, "h1")
    headings = [n.text(strip=True) for n in parser.css("h2, h3, h4") if n.text(strip=True)]

    _strip_boilerplate(parser)
    body_node = parser.css_first("article") or parser.css_first("main") or parser.body
    body_text = body_node.text(separator=" ", strip=True) if body_node else ""
    body_text = re.sub(r"\s+", " ", body_text).strip()
    word_count = len(body_text.split())

    query_lower = target_query.lower()
    target_in_title = query_lower in title.lower()
    target_in_h1 = query_lower in h1.lower()

    occurrences = body_text.lower().count(query_lower)
    target_density = (occurrences / word_count * 100.0) if word_count > 0 else 0.0

    suggestions: list[str] = []
    if not target_in_title:
        suggestions.append(f'Add "{target_query}" to the page title.')
    if not target_in_h1:
        suggestions.append(f'Add "{target_query}" to the H1 heading.')
    if target_density < 0.5:
        suggestions.append(
            f'Keyword density is {target_density:.2f}% (target: 0.5-1.5%). '
            "Use the phrase more naturally in the body text."
        )
    if word_count < 1500:
        suggestions.append(
            f"Page has {word_count} words. Consider expanding to 1500+ for competitive queries."
        )
    if len(headings) < 3:
        suggestions.append("Add more subheadings (H2/H3) to improve structure and scannability.")
    if not meta_desc:
        suggestions.append("Meta description is missing. Add one to improve CTR in search results.")
    elif len(meta_desc) < 100:
        suggestions.append(
            f"Meta description is short ({len(meta_desc)} chars). Aim for 140-160 characters."
        )

    return OnPageAudit(
        url=page_url,
        title=title,
        meta_description=meta_desc,
        h1=h1,
        headings=headings,
        word_count=word_count,
        target_in_title=target_in_title,
        target_in_h1=target_in_h1,
        target_density=round(target_density, 4),
        suggestions=suggestions,
    )
