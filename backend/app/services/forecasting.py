"""
Sales forecasting and seasonal pattern detection built on the synthetic
(or eventually real) monthly sales history. Uses Holt-Winters exponential
smoothing, which handles trend + seasonality without needing a large
training set the way a neural forecaster would.
"""
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from app.services.data_loader import category_series

FORECAST_HORIZON_MONTHS = 3
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def forecast_sales(category: str) -> dict:
    series = category_series(category)
    if len(series) < 24:
        raise ValueError("Not enough history to forecast (need >= 24 months)")

    model = ExponentialSmoothing(
        series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    )
    fit = model.fit(optimized=True)
    forecast_values = fit.forecast(FORECAST_HORIZON_MONTHS)

    history = [
        {"date": d.strftime("%Y-%m-%d"), "units": round(float(v), 1), "is_forecast": False}
        for d, v in series.items()
    ]
    forecast = [
        {"date": d.strftime("%Y-%m-%d"), "units": round(float(v), 1), "is_forecast": True}
        for d, v in forecast_values.items()
    ]

    return {
        "category": category,
        "method": "Holt-Winters exponential smoothing (additive trend + seasonality)",
        "history": history,
        "forecast": forecast,
    }


def forecast_change_pct(category: str) -> float:
    """Percent change from the last actual month to the final forecast month."""
    result = forecast_sales(category)
    last_actual = result["history"][-1]["units"]
    last_forecast = result["forecast"][-1]["units"]
    if last_actual == 0:
        return 0.0
    return round((last_forecast - last_actual) / last_actual * 100, 1)


def seasonal_pattern(category: str) -> dict:
    series = category_series(category)
    monthly_avg = series.groupby(series.index.month).mean()
    overall_avg = monthly_avg.mean()

    points = []
    for month_num in range(1, 13):
        avg_units = float(monthly_avg.get(month_num, 0.0))
        index = round(avg_units / overall_avg * 100, 1) if overall_avg else 100.0
        points.append({
            "month": MONTH_NAMES[month_num - 1],
            "avg_units": round(avg_units, 1),
            "index": index,
        })

    peak = max(points, key=lambda p: p["index"])
    low = min(points, key=lambda p: p["index"])

    return {
        "category": category,
        "peak_month": peak["month"],
        "low_month": low["month"],
        "points": points,
    }
