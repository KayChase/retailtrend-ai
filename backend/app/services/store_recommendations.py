"""
Generates per-product store operations recommendations (order more, expand
shelf space, adjust placement, etc.) from each product's Google-Trends-based
demand trend. Calls Claude once per department (batched, not once per
product) for natural-language recommendations when ANTHROPIC_API_KEY is
configured; falls back to deterministic threshold-based rules per product
otherwise, or per-product if Claude's response is missing/malformed for a
particular item.
"""
import json
import time
from typing import Optional

import anthropic

from app.config import ANTHROPIC_API_KEY, CATEGORY_LABELS
from app.models.schemas import StoreRecommendation
from app.services import weather
from app.services.product_trends import get_product_trends

MODEL = "claude-opus-4-7"

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

_CACHE_TTL_SECONDS = 60 * 60
_cache: dict[str, tuple[float, object]] = {}


def clear_cache() -> None:
    _cache.clear()


def _cached(key: str, builder):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < _CACHE_TTL_SECONDS:
        return hit[1]
    value = builder()
    _cache[key] = (now, value)
    return value


def rule_based_recommendation(product: str, trend_pct: float, weather_boost: Optional[float]) -> dict:
    effective_pct = trend_pct + (weather_boost or 0)

    if effective_pct >= 40:
        priority, action = "high", "Increase Stock & Expand Placement"
        demand, order_more, increase_facings = "Rising sharply", True, True
        placement = "Move to an endcap or eye-level shelf to capture the surge in demand."
    elif effective_pct >= 15:
        priority, action = "medium", "Order More"
        demand, order_more, increase_facings = "Rising", True, False
        placement = "Keep current placement, but consider a secondary display near checkout."
    elif effective_pct > -15:
        priority, action = "low", "Maintain Current Stock"
        demand, order_more, increase_facings = "Stable", False, False
        placement = "No placement changes needed right now."
    elif effective_pct > -40:
        priority, action = "medium", "Reduce Future Orders"
        demand, order_more, increase_facings = "Declining", False, False
        placement = "Consolidate facings to free up space for trending items."
    else:
        priority, action = "high", "Reduce Stock & Reconsider Placement"
        demand, order_more, increase_facings = "Declining sharply", False, False
        placement = "Move to a less prominent shelf position or a clearance display."

    reasoning = f"Search interest for {product} has changed {trend_pct}% recently"
    if weather_boost:
        reasoning += f", and the 7-day weather outlook adds roughly {weather_boost:+.1f}% expected demand"
    reasoning += f", which points to {demand.lower()} demand."

    return {
        "expected_demand": demand,
        "priority": priority,
        "action": action,
        "order_more": order_more,
        "increase_facings": increase_facings,
        "placement_suggestion": placement,
        "reasoning": reasoning,
    }


def _claude_recommendations(
    label: str, products: list[dict], weather_boosts: dict[str, Optional[float]]
) -> Optional[dict]:
    """products: [{product, change_pct, ...}]. Returns {product: {fields}} or None."""
    if _client is None:
        return None

    lines = []
    for p in products:
        boost = weather_boosts.get(p["product"])
        weather_note = (
            f"; 7-day weather outlook suggests a {boost:+.1f}% demand adjustment" if boost else ""
        )
        lines.append(f"- {p['product']}: {p['change_pct']}% search interest change{weather_note}")
    items = "\n".join(lines)
    prompt = (
        f"You are a retail merchandising analyst for the {label} department. "
        "For each product below, decide on a store operations recommendation based on its "
        f"recent Google search interest trend:\n{items}\n\n"
        "Respond with ONLY a JSON array (no markdown fences, no prose before or after), one object "
        "per product, each with exactly these fields: "
        '"product" (string, must match exactly), "expected_demand" (short phrase like "Rising sharply", '
        '"Stable", or "Declining"), "priority" ("high", "medium", or "low"), "action" (short label, '
        'max 6 words), "order_more" (boolean), "increase_facings" (boolean, whether to give the product '
        'more shelf space/locations), "placement_suggestion" (one sentence), and "reasoning" (one '
        "sentence explaining the recommendation using the trend data)."
    )
    try:
        response = _client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            return None
        return {item["product"]: item for item in parsed if "product" in item}
    except (anthropic.APIError, json.JSONDecodeError, KeyError, TypeError):
        return None


def _build_recommendations(category: str, location: Optional[str]) -> list[StoreRecommendation]:
    label = CATEGORY_LABELS[category]
    product_trends = get_product_trends(category)
    weather_boosts = {p["product"]: weather.weather_boost_pct(p["product"], location) for p in product_trends}

    claude_by_product = _claude_recommendations(label, product_trends, weather_boosts) or {}

    recommendations = []
    for item in product_trends:
        product = item["product"]
        trend_pct = item["change_pct"]
        w_boost = weather_boosts.get(product)
        claude_fields = claude_by_product.get(product)

        if claude_fields is not None:
            try:
                recommendations.append(
                    StoreRecommendation(
                        product=product,
                        trend_change_pct=trend_pct,
                        weather_boost_pct=w_boost,
                        expected_demand=str(claude_fields["expected_demand"]),
                        priority=str(claude_fields["priority"]),
                        action=str(claude_fields["action"]),
                        order_more=bool(claude_fields["order_more"]),
                        increase_facings=bool(claude_fields["increase_facings"]),
                        placement_suggestion=str(claude_fields["placement_suggestion"]),
                        reasoning=str(claude_fields["reasoning"]),
                        source="claude",
                    )
                )
                continue
            except (KeyError, TypeError):
                pass  # fall through to the rule-based path for this product

        fallback = rule_based_recommendation(product, trend_pct, w_boost)
        recommendations.append(
            StoreRecommendation(
                product=product,
                trend_change_pct=trend_pct,
                weather_boost_pct=w_boost,
                source="rule-based",
                **fallback,
            )
        )

    return recommendations


def get_store_recommendations(category: str, location: Optional[str] = None) -> list[StoreRecommendation]:
    cache_key = f"store-recs:{category}:{(location or 'default').lower()}"
    return _cached(cache_key, lambda: _build_recommendations(category, location))
