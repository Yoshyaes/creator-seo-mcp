from __future__ import annotations

from creator_seo_mcp.config import load_revenue_config


def test_load_revenue_config_defaults(monkeypatch):
    monkeypatch.delenv("CREATOR_SEO_SITE_RPM", raising=False)
    monkeypatch.delenv("CREATOR_SEO_AFFILIATE_CATEGORIES", raising=False)
    monkeypatch.delenv("CREATOR_SEO_CTR_CURVE", raising=False)

    config = load_revenue_config()
    assert config.site_rpm == 15.0
    assert config.affiliate_categories == {}


def test_load_revenue_config_reads_env(monkeypatch):
    monkeypatch.setenv("CREATOR_SEO_SITE_RPM", "22.0")
    monkeypatch.setenv("CREATOR_SEO_AFFILIATE_CATEGORIES", '{"gaming-deals": 2.0}')

    config = load_revenue_config()
    assert config.site_rpm == 22.0
    assert config.affiliate_categories == {"gaming-deals": 2.0}


def test_site_rpm_override_preserves_affiliate_and_ctr_settings(monkeypatch):
    """Overriding just site_rpm (as get_top_opportunities does) must not silently
    drop the affiliate multipliers or custom CTR curve configured via env vars."""
    monkeypatch.setenv("CREATOR_SEO_SITE_RPM", "15.0")
    monkeypatch.setenv("CREATOR_SEO_AFFILIATE_CATEGORIES", '{"gaming-deals": 2.0}')
    monkeypatch.setenv("CREATOR_SEO_CTR_CURVE", '{"1": 0.3, "2": 0.2}')

    config = load_revenue_config(site_rpm_override=30.0)

    assert config.site_rpm == 30.0
    assert config.affiliate_categories == {"gaming-deals": 2.0}
    assert config.ctr_curve == {1: 0.3, 2: 0.2}
