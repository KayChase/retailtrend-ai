"""
Generates synthetic monthly sales history per category/state so the
forecasting and heat map features work without needing a real CVS
sales feed. Deterministic (seeded) so results are reproducible.

Run with: python -m app.data.generate_sample_data
"""
import math
import random
from datetime import date

import pandas as pd

from app.config import CATEGORIES, STATES, SAMPLE_SALES_CSV

MONTHS_OF_HISTORY = 36  # 3 years

# (base_units, yearly_growth, seasonal_peak_month, seasonal_strength)
CATEGORY_PROFILE = {
    "allergy_medicine": (1200, 0.06, 4, 0.55),   # peaks spring (April)
    "bug_spray":        (600, 0.04, 6, 0.75),    # peaks summer (June)
    "melatonin":        (900, 0.10, 0, 0.20),    # mild winter bump
    "vitamin_d":        (700, 0.08, 11, 0.35),   # peaks winter (Dec)
    "sunscreen":        (1000, 0.05, 6, 0.85),   # strong summer peak
    "cold_flu":         (1500, 0.03, 0, 0.65),   # peaks Jan
    "cough_drops":      (800, 0.03, 0, 0.50),    # peaks Jan
    "hand_sanitizer":   (650, 0.02, 0, 0.15),    # fairly flat
}

# Relative population/store-density weighting so heat maps look plausible
STATE_WEIGHT = {
    "CA": 3.2, "TX": 2.8, "FL": 2.3, "NY": 2.1, "PA": 1.5,
    "IL": 1.4, "OH": 1.4, "GA": 1.3, "NC": 1.3, "MI": 1.3,
}
DEFAULT_WEIGHT = 0.6


def month_seasonal_multiplier(month_idx: int, peak_month: int, strength: float) -> float:
    # month_idx, peak_month are 0-11. Cosine curve centered on peak month.
    angle = 2 * math.pi * (month_idx - peak_month) / 12
    return 1 + strength * math.cos(angle)


def generate() -> pd.DataFrame:
    rng = random.Random(42)
    rows = []
    today = date.today().replace(day=1)
    start_month_index = today.year * 12 + today.month - MONTHS_OF_HISTORY

    for cat_key in CATEGORIES:
        base, growth, peak_month, strength = CATEGORY_PROFILE[cat_key]
        for m in range(MONTHS_OF_HISTORY):
            month_index = start_month_index + m
            year = month_index // 12
            month = month_index % 12 + 1
            d = date(year, month, 1)

            years_elapsed = m / 12
            trend = base * ((1 + growth) ** years_elapsed)
            seasonal = month_seasonal_multiplier(month - 1, peak_month, strength)

            for state in STATES:
                weight = STATE_WEIGHT.get(state, DEFAULT_WEIGHT)
                noise = rng.uniform(0.9, 1.1)
                units = trend * seasonal * weight * noise / 10
                rows.append({
                    "date": d.isoformat(),
                    "category": cat_key,
                    "region": state,
                    "units_sold": round(max(units, 0), 1),
                })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate()
    SAMPLE_SALES_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAMPLE_SALES_CSV, index=False)
    print(f"Wrote {len(df)} rows to {SAMPLE_SALES_CSV}")
