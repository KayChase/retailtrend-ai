"""
Fetches Google-Trends-based search interest for individual products within a
department (e.g. "M&M's" under Candy & Snacks), so the dashboard can show
department-specific trending items instead of comparing whole departments
against each other. Falls back to a stable, seeded pseudo-trend per product
when Google Trends is unreachable, since there's no real per-product sales
history to derive a fallback from (only per-department history exists).
"""
import math
import random
import time
from datetime import date
from typing import Optional

from app.config import FEATURED_TOP_TREND_PCT, PRODUCT_SEASONALITY, PRODUCTS

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


def _chunk(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _change_pct(series) -> float:
    if series.empty or series.iloc[0] == 0:
        return 0.0
    return round((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100, 1)


def _fallback_change_pct(product: str, today: Optional[date] = None) -> float:
    """
    Deterministic per-product pseudo-trend, shaped by how close today is to the
    product's real-world peak month (e.g. "Fourth of July Decorations" spikes
    in early July, not "Pumpkin Decor"). Stable across reloads since both the
    seasonal component and the jitter are seeded, not purely random.
    """
    peak_month, strength = PRODUCT_SEASONALITY[product]
    current_month = (today or date.today()).month
    angle = 2 * math.pi * ((current_month - 1) - (peak_month - 1)) / 12
    seasonal_pct = math.cos(angle) * strength * 100

    rng = random.Random(hash(product) & 0xFFFFFFFF)
    jitter = rng.uniform(-8, 8)
    return round(seasonal_pct + jitter, 1)


def _fetch_chunk_live(products: list[str]) -> dict[str, float]:
    from pytrends.request import TrendReq

    pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
    pytrends.build_payload(products, timeframe="today 12-m", geo="US")
    df = pytrends.interest_over_time()
    if df.empty:
        raise ValueError("empty response")

    results = {}
    for product in products:
        monthly = df[product].resample("MS").mean().round(1)
        results[product] = _change_pct(monthly)
    return results


def get_product_trends(category: str) -> list[dict]:
    """Returns [{product, change_pct, source}] for every product in a department."""
    products = PRODUCTS[category]

    def build():
        results = []
        for chunk in _chunk(products, 5):
            try:
                live_values = _fetch_chunk_live(chunk)
                results.extend(
                    {"product": p, "change_pct": live_values[p], "source": "live"}
                    for p in chunk
                )
            except Exception:
                results.extend(
                    {"product": p, "change_pct": _fallback_change_pct(p), "source": "sample"}
                    for p in chunk
                )

        for item in results:
            if item["product"] in FEATURED_TOP_TREND_PCT:
                item["change_pct"] = FEATURED_TOP_TREND_PCT[item["product"]]
                item["source"] = "sample"

        return results

    return _cached(f"products:{category}", build)
