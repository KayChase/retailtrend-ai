from typing import Optional
from pydantic import BaseModel


class CategoryInfo(BaseModel):
    key: str
    label: str
    search_term: str


class TrendPoint(BaseModel):
    date: str
    value: float


class TrendSeries(BaseModel):
    category: str
    search_term: str
    change_pct: float
    source: str  # "live" or "sample"
    points: list[TrendPoint]


class RegionValue(BaseModel):
    region: str
    value: float


class RegionHeatMap(BaseModel):
    category: str
    source: str
    regions: list[RegionValue]


class SeasonalPoint(BaseModel):
    month: str
    avg_units: float
    index: float  # 100 = average month


class SeasonalPattern(BaseModel):
    category: str
    peak_month: str
    low_month: str
    points: list[SeasonalPoint]


class ForecastPoint(BaseModel):
    date: str
    units: float
    is_forecast: bool


class ForecastResult(BaseModel):
    category: str
    method: str
    history: list[ForecastPoint]
    forecast: list[ForecastPoint]


class Recommendation(BaseModel):
    category: str
    headline: str
    detail: str
    trend_change_pct: float
    forecast_change_pct: float
    source: str  # "claude" or "rule-based"


class DashboardResponse(BaseModel):
    categories: list[CategoryInfo]
    trends: list[TrendSeries]
    recommendations: list[Recommendation]
