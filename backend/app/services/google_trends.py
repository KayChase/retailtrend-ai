"""
Wraps pytrends (unofficial Google Trends API) to fetch search interest
over time and by region. Google Trends rate-limits aggressively and pytrends
has no official uptime guarantee, so every call falls back to a deterministic
synthetic series derived from the category's sales seasonality. This keeps
the dashboard usable in demos/offline dev while still hitting the real API
when it's reachable.
"""
import time
from datetime import datetime, timedelta
from functools import lru_cache

import pandas as pd

from app.config import CATEGORIES, STATES
from app.services.data_loader import category_series

_CACHE_TTL_SECONDS = 60 * 60  # Google Trends data doesn't need to be fresher than this
_cache: dict[str, tuple[float, object]] = {}


def _cached(key: str, builder):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < _CACHE_TTL_SECONDS:
        return hit[1]
    value = builder()
    _cache[key] = (now, value)
    return value


def _fallback_interest_over_time(search_term: str) -> pd.Series:
    """Derives a plausible 0-100 interest series from sales seasonality."""
    category = next((k for k, v in CATEGORIES.items() if v == search_term), None)
    if category is None:
        category = list(CATEGORIES.keys())[0]
    monthly_sales = category_series(category).tail(12)
    if monthly_sales.empty:
        return pd.Series(dtype=float)
    normalized = (monthly_sales / monthly_sales.max() * 100).round(1)
    return normalized


def get_interest_over_time(search_term: str) -> tuple[pd.Series, str]:
    """Returns (series indexed by date, source) where source is 'live' or 'sample'."""

    def build():
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
            pytrends.build_payload([search_term], timeframe="today 12-m", geo="US")
            df = pytrends.interest_over_time()
            if df.empty:
                raise ValueError("empty response")
            series = df[search_term]
            monthly = series.resample("MS").mean().round(1)
            return (monthly, "live")
        except Exception:
            return (_fallback_interest_over_time(search_term), "sample")

    return _cached(f"iot:{search_term}", build)


def get_interest_by_region(search_term: str) -> tuple[pd.Series, str]:
    """Returns (series indexed by US state abbreviation, source)."""

    def build():
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl="en-US", tz=360, timeout=(5, 10))
            pytrends.build_payload([search_term], timeframe="today 3-m", geo="US")
            df = pytrends.interest_by_region(resolution="REGION", inc_low_vol=True)
            if df.empty:
                raise ValueError("empty response")
            series = df[search_term]
            return (series, "live")
        except Exception:
            category = next((k for k, v in CATEGORIES.items() if v == search_term), None)
            if category is None:
                category = list(CATEGORIES.keys())[0]
            from app.services.data_loader import category_region_snapshot

            snapshot = category_region_snapshot(category).set_index("region")["units_sold"]
            normalized = (snapshot / snapshot.max() * 100).round(1)
            return (normalized, "sample")

    return _cached(f"ibr:{search_term}", build)
