# creator-seo-mcp

[![CI](https://github.com/Yoshyaes/creator-seo-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Yoshyaes/creator-seo-mcp/actions/workflows/ci.yml)

An MCP server for content creators that connects Google Search Console to your page content and ranks every SEO opportunity by estimated revenue, not vanity clicks.

Generic SEO tools surface raw GSC numbers. This one tells you which fix pays most, based on your actual display-ad RPM and affiliate commission rates.

## What it does

Six tools, designed to work together in a full creator-SEO workflow:

| Tool | Description |
|---|---|
| `get_striking_distance_keywords` | Queries ranking at positions 4-15 with real impression volume, the ranking page, and the gap to page 1 |
| `get_page_performance` | Full GSC picture for one URL: clicks, impressions, CTR, position, and the queries driving it |
| `analyze_content_decay` | Flags pages losing clicks or impressions month-over-month |
| `audit_page_onpage` | Fetches a URL, reads title/meta/headings/body, compares against a target query, and proposes concrete edits |
| `find_cannibalization` | Detects queries where multiple pages compete, splitting authority |
| `get_top_opportunities` | The headline call: combines all signals, weights by revenue, returns a single ranked action list |

## Install

```bash
uvx creator-seo-mcp
```

Or with pip:

```bash
pip install creator-seo-mcp
```

## Setup

### 1. Google Search Console credentials

Follow [docs/gsc-setup.md](docs/gsc-setup.md) to:
- Enable the Search Console API in Google Cloud
- Create an OAuth 2.0 Desktop client
- Download `credentials.json`

### 2. Claude Desktop config

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "creator-seo-mcp": {
      "command": "uvx",
      "args": ["creator-seo-mcp"],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/path/to/credentials.json",
        "CREATOR_SEO_SITE_RPM": "15"
      }
    }
  }
}
```

### 3. Claude Code config

```bash
claude mcp add creator-seo-mcp uvx creator-seo-mcp \
  -e GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json \
  -e CREATOR_SEO_SITE_RPM=15
```

### 4. Revenue config (optional but recommended)

Set your display-ad RPM so opportunities are ranked by real dollars:

```bash
export CREATOR_SEO_SITE_RPM=22          # your Mediavine/Raptive RPM
export CREATOR_SEO_AFFILIATE_CATEGORIES='{"gaming-deals": 2.0}'
```

See `.env.example` for all options.

## Example agent prompts

- "Show me my top five revenue-weighted SEO opportunities for this week."
- "Which of my posts are losing traffic compared to last month?"
- "My Baldur's Gate 3 build guide is stuck on page 2. Audit it against its main keyword and tell me what to fix."
- "Find any posts that are competing with each other for the same search term."
- "What is the on-page gap between this article and the query it is trying to rank for?"

## Two Average Gamers case study

Real output from `get_top_opportunities`, run live against [Two Average Gamers](https://www.twoaveragegamers.com/) (a top-200 gaming blog on Mediavine display ads and Amazon affiliate links) on 2026-08-25, over the trailing 28 days (392K impressions, 3.5K clicks per Search Console).

This is the actual "before" baseline, not a mockup. Dollar estimates use the default $15 RPM placeholder (set `CREATOR_SEO_SITE_RPM` to your real network RPM for accurate figures). Out of 147 scored opportunities across all three signal types, the top 5 by estimated revenue:

| # | Type | Page | Query | Finding |
|---|---|---|---|---|
| 1 | Striking distance | [best-letterboxd-alternatives...](https://www.twoaveragegamers.com/best-letterboxd-alternatives-for-gamers-who-track-everything-2026/) | "letterboxd for games" | Position 4.6, 97K impressions, 1.6-position gap to page 1 |
| 2 | Cannibalization | same page + 3 others | "letterboxd for games" | 4 TAG pages splitting 99.8K impressions on the same query |
| 3 | Striking distance | [backloggd-review](https://www.twoaveragegamers.com/backloggd-review/) | "backloggd" | Position 5.5, 11.4K impressions, 2.5-position gap to page 1 |
| 4 | Cannibalization | same page + 2 others | "backloggd" | 3 TAG pages splitting 15.1K impressions on the same query |
| 5 | Striking distance | [backloggd-vs-gg-vs-savepoint](https://www.twoaveragegamers.com/backloggd-vs-gg-vs-savepoint/) | "backloggd" | Position 5.5, 3.7K impressions, 2.5-position gap to page 1 |

`analyze_content_decay` also flagged 40 pages losing clicks month-over-month on this run, the worst being a 100% drop (10 clicks to 0) on a Palworld lawsuit post and a 61% drop on a Palworld tower-boss guide, both worth a content refresh before the traffic they had is gone for good.

**Update (2026-08-25):** the title/H1 edits for the two striking-distance opportunities above are live. Re-running `audit_page_onpage` against the real pages confirms it:

| Page | Target query | In title? | In H1? | Remaining suggestions |
|---|---|---|---|---|
| [best-letterboxd-alternatives...](https://www.twoaveragegamers.com/best-letterboxd-alternatives-for-gamers-who-track-everything-2026/) | "letterboxd for games" | ✅ | ✅ | none |
| [backloggd-review](https://www.twoaveragegamers.com/backloggd-review/) | "backloggd" | ✅ | ✅ | none |
| [backloggd-vs-gg-vs-savepoint](https://www.twoaveragegamers.com/backloggd-vs-gg-vs-savepoint/) | "backloggd" | ✅ | ✅ | none |

No position or traffic movement to report yet, and that's expected, not a null result: Search Console's data has a 2-3 day freshness lag, so a same-day re-pull still covers the identical `2026-07-26` to `2026-08-22` window as the original baseline above, before any of these edits existed. Google also needs to re-crawl and re-rank the pages, which typically takes longer than the raw data lag. This section will be updated again once a GSC pull actually covers the post-edit period (realistically 2-3 weeks out) with the real position and click change, not before.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

<!-- mcp-name: io.github.Yoshyaes/creator-seo-mcp -->
