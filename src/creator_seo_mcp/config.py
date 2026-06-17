from __future__ import annotations

import json
import os

from .models import RevenueConfig


def load_revenue_config(override: RevenueConfig | None = None) -> RevenueConfig:
    if override is not None:
        return override

    site_rpm = float(os.environ.get("CREATOR_SEO_SITE_RPM", "15.0"))

    affiliate_raw = os.environ.get("CREATOR_SEO_AFFILIATE_CATEGORIES", "{}")
    affiliate_categories: dict[str, float] = json.loads(affiliate_raw)

    ctr_raw = os.environ.get("CREATOR_SEO_CTR_CURVE", "")
    if ctr_raw:
        raw_curve: dict[str, float] = json.loads(ctr_raw)
        ctr_curve = {int(k): v for k, v in raw_curve.items()}
    else:
        ctr_curve = RevenueConfig().ctr_curve

    return RevenueConfig(
        site_rpm=site_rpm,
        affiliate_categories=affiliate_categories,
        ctr_curve=ctr_curve,
    )


def credentials_path() -> str:
    path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "")
    if not path:
        raise ValueError(
            "GOOGLE_CREDENTIALS_PATH env var is not set. "
            "See docs/gsc-setup.md for setup instructions."
        )
    return path


def token_path() -> str:
    default = os.path.expanduser("~/.creator-seo-mcp/token.json")
    return os.environ.get("CREATOR_SEO_TOKEN_PATH", default)
