from fastapi import APIRouter, HTTPException

from app.config import CATEGORIES
from app.models.schemas import (
    ForecastAccuracy,
    ForecastPoint,
    ForecastResult,
    SeasonalPattern,
    SeasonalPoint,
)
from app.services.forecast_accuracy import get_accuracy, log_forecast
from app.services.forecasting import forecast_sales, seasonal_pattern

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


@router.get("/{category}", response_model=ForecastResult)
def get_forecast(category: str) -> ForecastResult:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    try:
        result = forecast_sales(category)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    log_forecast(category, result)

    return ForecastResult(
        category=result["category"],
        method=result["method"],
        history=[ForecastPoint(**p) for p in result["history"]],
        forecast=[ForecastPoint(**p) for p in result["forecast"]],
    )


@router.get("/{category}/accuracy", response_model=ForecastAccuracy)
def get_forecast_accuracy(category: str) -> ForecastAccuracy:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    return ForecastAccuracy(**get_accuracy(category))


@router.get("/{category}/seasonal", response_model=SeasonalPattern)
def get_seasonal_pattern(category: str) -> SeasonalPattern:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    result = seasonal_pattern(category)
    return SeasonalPattern(
        category=result["category"],
        peak_month=result["peak_month"],
        low_month=result["low_month"],
        points=[SeasonalPoint(**p) for p in result["points"]],
    )
