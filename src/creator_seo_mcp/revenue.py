from __future__ import annotations

import math

from .models import CannibalizationGroup, DecayResult, Opportunity, RevenueConfig, StrikingKeyword


def _affiliate_multiplier(page_url: str, config: RevenueConfig) -> float:
    for prefix, multiplier in config.affiliate_categories.items():
        if prefix in page_url:
            return multiplier
    return 1.0


def _ctr_at(position: float, curve: dict[int, float]) -> float:
    pos_int = min(max(1, math.floor(position)), max(curve.keys()))
    return curve.get(pos_int, 0.01)


def score_striking(keyword: StrikingKeyword, config: RevenueConfig) -> Opportunity:
    target_position = max(1, math.floor(keyword.position) - 3)
    ctr_gain = _ctr_at(target_position, config.ctr_curve) - _ctr_at(keyword.position, config.ctr_curve)
    ctr_gain = max(0.0, ctr_gain)
    est_traffic_gain = keyword.impressions * ctr_gain
    page_value_per_click = (config.site_rpm / 1000.0) * _affiliate_multiplier(keyword.page, config)
    est_value = est_traffic_gain * page_value_per_click

    return Opportunity(
        type="striking",
        page=keyword.page,
        query=keyword.query,
        est_traffic_gain=round(est_traffic_gain, 2),
        est_value=round(est_value, 4),
        score=round(est_value, 4),
        recommended_action=(
            f'Add "{keyword.query}" to the title and H1. '
            f"Currently at position {keyword.position:.1f}, gap to page 1: {keyword.gap_to_page1:.1f} positions."
        ),
    )


def score_decay(decay: DecayResult, config: RevenueConfig) -> Opportunity:
    lost_clicks = max(0, decay.prior_clicks - decay.recent_clicks)
    page_value_per_click = (config.site_rpm / 1000.0) * _affiliate_multiplier(decay.page, config)
    est_value = lost_clicks * page_value_per_click

    return Opportunity(
        type="decay",
        page=decay.page,
        query=None,
        est_traffic_gain=float(lost_clicks),
        est_value=round(est_value, 4),
        score=round(est_value, 4),
        recommended_action=(
            f"Refresh and expand this content. Traffic dropped {decay.pct_change:.1f}% "
            f"({decay.prior_clicks} to {decay.recent_clicks} clicks)."
        ),
    )


def score_cannibalization(group: CannibalizationGroup, config: RevenueConfig) -> Opportunity:
    page_value = (config.site_rpm / 1000.0) * _affiliate_multiplier(group.primary_page, config)
    est_value = group.total_impressions * 0.02 * page_value

    return Opportunity(
        type="cannibalization",
        page=group.primary_page,
        query=group.query,
        est_traffic_gain=round(group.total_impressions * 0.02, 2),
        est_value=round(est_value, 4),
        score=round(est_value, 4),
        recommended_action=(
            f'Consolidate or differentiate pages competing for "{group.query}". '
            f"Competing pages: {', '.join(group.competing_pages[:3])}."
        ),
    )
