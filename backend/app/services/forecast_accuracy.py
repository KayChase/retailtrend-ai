"""
Tracks forecast accuracy over time. Every time a forecast is generated for a
category, the predicted values for its future months are logged — but
logging never overwrites an existing entry, so we're always comparing
against the prediction that was actually made ahead of time, not one
regenerated right before the comparison. Once real time (and data) catches
up to a previously-forecasted month, that prediction can be checked against
what actually happened, so accuracy will legitimately show nothing until
enough time has passed for at least one forecasted month to mature.
"""
import json
from datetime import datetime, timezone

from app.config import FORECAST_LOG_JSON
from app.services.data_loader import category_series


def _load_log() -> dict:
    if not FORECAST_LOG_JSON.exists():
        return {}
    with open(FORECAST_LOG_JSON) as f:
        return json.load(f)


def _save_log(log: dict) -> None:
    FORECAST_LOG_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(FORECAST_LOG_JSON, "w") as f:
        json.dump(log, f, indent=2)


def clear_log() -> None:
    """
    Wipes all logged predictions. Must be called whenever the underlying
    sales data source changes (upload/reset) — otherwise a prediction logged
    against one dataset could later get "matured" against actuals from a
    completely different dataset, which is meaningless.
    """
    if FORECAST_LOG_JSON.exists():
        FORECAST_LOG_JSON.unlink()


def log_forecast(category: str, forecast_result: dict) -> None:
    log = _load_log()
    changed = False
    for point in forecast_result["forecast"]:
        key = f"{category}|{point['date']}"
        if key in log:
            continue
        log[key] = {
            "category": category,
            "forecast_date": point["date"],
            "predicted_units": point["units"],
            "logged_at": datetime.now(timezone.utc).isoformat(),
            "method": forecast_result["method"],
        }
        changed = True
    if changed:
        _save_log(log)


def get_accuracy(category: str) -> dict:
    log = _load_log()
    entries = [v for v in log.values() if v["category"] == category]

    actual_series = category_series(category)
    actual_by_date = {d.strftime("%Y-%m-%d"): float(v) for d, v in actual_series.items()}

    matured = []
    pending_count = 0
    for entry in sorted(entries, key=lambda e: e["forecast_date"]):
        actual = actual_by_date.get(entry["forecast_date"])
        if actual is None:
            pending_count += 1
            continue
        predicted = entry["predicted_units"]
        error_pct = round((predicted - actual) / actual * 100, 1) if actual else 0.0
        matured.append(
            {
                "forecast_date": entry["forecast_date"],
                "predicted_units": predicted,
                "actual_units": actual,
                "error_pct": error_pct,
            }
        )

    mape = None
    if matured:
        mape = round(sum(abs(m["error_pct"]) for m in matured) / len(matured), 1)

    return {
        "category": category,
        "matured": matured,
        "mape": mape,
        "pending_count": pending_count,
    }
