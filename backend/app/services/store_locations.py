"""
Store-level drill-down for the regional heat map. Store addresses come from a
user-provided CSV of store locations (app/data/store_locations.csv) — real
addresses, but there's no real per-store sales source behind them. So every
per-store trend/recommendation applies a small, deterministic variation on
top of the existing category-level data — clearly labeled as simulated on
every response.
"""
import csv
from functools import lru_cache
from typing import Optional
import random

from app.config import STORE_LOCATIONS_CSV
from app.models.schemas import StoreRecommendation
from app.services import weather
from app.services.product_trends import get_product_trends
from app.services.store_recommendations import rule_based_recommendation


@lru_cache(maxsize=1)
def _stores_by_state() -> dict[str, list[dict]]:
    by_state: dict[str, list[dict]] = {}
    counters: dict[str, int] = {}

    if not STORE_LOCATIONS_CSV.exists():
        return by_state

    with open(STORE_LOCATIONS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            state = row["State"].strip().upper()
            if not state:
                continue
            counters[state] = counters.get(state, 0) + 1
            by_state.setdefault(state, []).append(
                {
                    "store_id": f"{state}-{counters[state]:04d}",
                    "city": row["City"].strip(),
                    "address": row["Address"].strip(),
                }
            )

    for state, stores in by_state.items():
        stores.sort(key=lambda s: (s["city"], s["address"]))

    return by_state


def list_stores(state: str) -> list[dict]:
    return _stores_by_state().get(state.upper(), [])


def _store_ids(state: str) -> set[str]:
    return {s["store_id"] for s in list_stores(state)}


def _store_jitter(store_id: str, product: str) -> float:
    """Deterministic +/-15% per-store variation so each store differs slightly."""
    rng = random.Random(f"{store_id}:{product}")
    return round(rng.uniform(-15, 15), 1)


def get_store_product_trends(state: str, store_id: str, category: str) -> list[dict]:
    if store_id not in _store_ids(state):
        raise ValueError(f"Unknown store '{store_id}' for state '{state.upper()}'")

    base = get_product_trends(category)
    return [
        {
            "product": item["product"],
            "change_pct": round(item["change_pct"] + _store_jitter(store_id, item["product"]), 1),
            "source": item["source"],
        }
        for item in base
    ]


def get_store_recommendations(
    state: str, store_id: str, category: str, location: Optional[str] = None
) -> list[StoreRecommendation]:
    trends = get_store_product_trends(state, store_id, category)
    recommendations = []
    for item in trends:
        product = item["product"]
        trend_pct = item["change_pct"]
        w_boost = weather.weather_boost_pct(product, location)
        fields = rule_based_recommendation(product, trend_pct, w_boost)
        recommendations.append(
            StoreRecommendation(
                product=product,
                trend_change_pct=trend_pct,
                weather_boost_pct=w_boost,
                source="rule-based",
                **fields,
            )
        )
    return recommendations
