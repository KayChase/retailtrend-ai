"""
Generates one-paragraph business recommendations per category by combining
Google Trends interest, sales trend, and forecast direction. Calls Claude for
natural-language narrative when ANTHROPIC_API_KEY is configured; otherwise
falls back to a deterministic rule-based recommendation so the dashboard
works fully offline / without API credentials.
"""
from typing import Optional

import anthropic

from app.config import ANTHROPIC_API_KEY, CATEGORIES
from app.models.schemas import Recommendation
from app.services.forecasting import forecast_change_pct
from app.services.google_trends import get_interest_over_time

MODEL = "claude-opus-4-7"

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def _trend_change_pct(search_term: str) -> float:
    series, _source = get_interest_over_time(search_term)
    if series.empty or series.iloc[0] == 0:
        return 0.0
    return round((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100, 1)


def _rule_based_recommendation(label: str, trend_pct: float, forecast_pct: float) -> tuple[str, str]:
    rising = trend_pct > 5 and forecast_pct > 0
    falling = trend_pct < -5 and forecast_pct < 0
    if rising:
        headline = f"{label}: demand is rising"
        detail = (
            f"Search interest for {label.lower()} is up {trend_pct}% and the sales forecast "
            f"projects a further {forecast_pct}% change next quarter. Consider increasing "
            f"endcap displays and checking inventory levels ahead of the seasonal peak."
        )
    elif falling:
        headline = f"{label}: demand is cooling"
        detail = (
            f"Search interest for {label.lower()} is down {abs(trend_pct)}% and the forecast "
            f"shows a further {forecast_pct}% decline. Consider reducing incoming orders and "
            f"reallocating shelf space toward rising categories."
        )
    else:
        headline = f"{label}: demand is stable"
        detail = (
            f"Search interest and forecasted sales for {label.lower()} show no strong directional "
            f"signal right now (trend {trend_pct}%, forecast {forecast_pct}%). Maintain current "
            f"stocking levels and monitor for seasonal shifts."
        )
    return headline, detail


def _claude_recommendation(label: str, trend_pct: float, forecast_pct: float) -> Optional[tuple[str, str]]:
    if _client is None:
        return None
    prompt = (
        f"You are a retail merchandising analyst. Category: {label}. "
        f"Google search interest change over the last 12 months: {trend_pct}%. "
        f"Forecasted sales change over the next 3 months: {forecast_pct}%. "
        "Write a short, actionable recommendation for a store employee dashboard. "
        "Respond with exactly a headline (max 8 words) on the first line, a blank line, "
        "then a 2-3 sentence business recommendation. No markdown, no labels like 'Headline:'."
    )
    try:
        response = _client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        if not text:
            return None
        parts = text.split("\n\n", 1)
        if len(parts) == 1:
            parts = text.split("\n", 1)
        headline = parts[0].strip()
        detail = parts[1].strip() if len(parts) > 1 else headline
        return headline, detail
    except anthropic.APIError:
        return None


def generate_recommendation(category: str) -> Recommendation:
    label = category.replace("_", " ").title()
    search_term = CATEGORIES[category]
    trend_pct = _trend_change_pct(search_term)
    forecast_pct = forecast_change_pct(category)

    claude_result = _claude_recommendation(label, trend_pct, forecast_pct)
    if claude_result is not None:
        headline, detail = claude_result
        source = "claude"
    else:
        headline, detail = _rule_based_recommendation(label, trend_pct, forecast_pct)
        source = "rule-based"

    return Recommendation(
        category=category,
        headline=headline,
        detail=detail,
        trend_change_pct=trend_pct,
        forecast_change_pct=forecast_pct,
        source=source,
    )


def generate_all_recommendations() -> list[Recommendation]:
    return [generate_recommendation(category) for category in CATEGORIES]
