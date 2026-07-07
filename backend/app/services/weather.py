"""
Fetches a 7-day weather outlook via Open-Meteo (free, no API key required)
for a user-chosen location, and derives a per-product demand boost for
weather-sensitive products (e.g. sunscreen sells more ahead of a heat wave,
cold medicine ahead of a cold snap). Falls back to generic monthly climate
averages if the API is unreachable, consistent with the rest of the app's
live/sample pattern.
"""
import random
import time
from datetime import date, timedelta
from typing import Optional

import requests

from app.config import DEFAULT_WEATHER_LOCATION, WEATHER_SENSITIVITY

_CACHE_TTL_SECONDS = 60 * 60
_cache: dict[str, tuple[float, object]] = {}

# Generic continental-US monthly climate normals (avg high/low °F), used only
# as a fallback when the live weather API can't be reached.
MONTHLY_AVG_TEMPS_F = {
    1: (40, 25), 2: (44, 28), 3: (53, 35), 4: (63, 43), 5: (72, 52),
    6: (81, 61), 7: (86, 66), 8: (85, 65), 9: (78, 58), 10: (66, 47),
    11: (54, 37), 12: (42, 27),
}


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


def _fallback_forecast(today: Optional[date] = None) -> list[dict]:
    today = today or date.today()
    rng = random.Random(today.toordinal())
    days = []
    for i in range(7):
        d = today + timedelta(days=i)
        avg_high, avg_low = MONTHLY_AVG_TEMPS_F[d.month]
        jitter = rng.uniform(-4, 4)
        days.append(
            {
                "date": d.isoformat(),
                "temp_max": round(avg_high + jitter, 1),
                "temp_min": round(avg_low + jitter, 1),
                "precipitation_probability": round(rng.uniform(10, 45), 0),
            }
        )
    return days


def _geocode_query(name: str) -> Optional[dict]:
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": name, "count": 1, "language": "en", "format": "json"},
        timeout=5,
    )
    resp.raise_for_status()
    results = resp.json().get("results") or []
    if not results:
        return None
    top = results[0]
    region = top.get("admin1") or top.get("country") or ""
    return {"name": f"{top['name']}, {region}".strip(", "), "lat": top["latitude"], "lon": top["longitude"]}


def geocode_location(query: str) -> Optional[dict]:
    def build():
        # Open-Meteo's geocoder often returns zero results for "City, ST" but
        # succeeds on "City" alone (confirmed: "New York, NY" fails, "New York"
        # doesn't) — so retry with just the part before the first comma before
        # giving up and falling back to sample data.
        try:
            result = _geocode_query(query)
            if result is not None:
                return result
        except Exception:
            pass

        if "," in query:
            try:
                return _geocode_query(query.split(",")[0].strip())
            except Exception:
                return None
        return None

    return _cached(f"geocode:{query.lower()}", build)


def get_weather_outlook(location: Optional[str] = None) -> dict:
    location = location or DEFAULT_WEATHER_LOCATION

    def build():
        geo = geocode_location(location)
        if geo is None:
            return {"location": location, "source": "sample", "days": _fallback_forecast()}
        try:
            resp = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": geo["lat"],
                    "longitude": geo["lon"],
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "temperature_unit": "fahrenheit",
                    "forecast_days": 7,
                    "timezone": "auto",
                },
                timeout=5,
            )
            resp.raise_for_status()
            daily = resp.json()["daily"]
            days = [
                {
                    "date": d,
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "precipitation_probability": daily["precipitation_probability_max"][i],
                }
                for i, d in enumerate(daily["time"])
            ]
            return {"location": geo["name"], "source": "live", "days": days}
        except Exception:
            return {"location": geo["name"], "source": "sample", "days": _fallback_forecast()}

    return _cached(f"outlook:{location.lower()}", build)


def _intensity(weather_type: str, avg_max: float, avg_min: float) -> float:
    if weather_type == "hot":
        if avg_max >= 90:
            return 1.0
        if avg_max >= 80:
            return 0.6
        if avg_max >= 70:
            return 0.2
        return -0.3
    if weather_type == "cold":
        if avg_min <= 25:
            return 1.0
        if avg_min <= 40:
            return 0.6
        if avg_min <= 55:
            return 0.2
        return -0.3
    return 0.0


def weather_boost_pct(product: str, location: Optional[str] = None) -> Optional[float]:
    """Returns a % demand boost/drag for weather-sensitive products, or None if not applicable."""
    sensitivity = WEATHER_SENSITIVITY.get(product)
    if sensitivity is None:
        return None

    weather_type, strength = sensitivity
    days = get_weather_outlook(location)["days"]
    if not days:
        return None

    avg_max = sum(d["temp_max"] for d in days) / len(days)
    avg_min = sum(d["temp_min"] for d in days) / len(days)
    intensity = _intensity(weather_type, avg_max, avg_min)
    return round(intensity * strength * 60, 1)
