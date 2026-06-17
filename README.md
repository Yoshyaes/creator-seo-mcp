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

*Before/after numbers to be added after dogfood phase.*

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

<!-- mcp-name: io.github.Yoshyaes/creator-seo-mcp -->
