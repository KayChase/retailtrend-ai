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


class ProductTrend(BaseModel):
    product: str
    change_pct: float
    source: str  # "live" or "sample"


class CategoryProductTrends(BaseModel):
    category: str
    products: list[ProductTrend]


class StoreRecommendation(BaseModel):
    product: str
    trend_change_pct: float
    weather_boost_pct: Optional[float] = None
    expected_demand: str  # e.g. "Rising sharply", "Stable", "Declining"
    priority: str  # "high", "medium", "low"
    action: str  # short label, e.g. "Increase Stock & Expand Placement"
    order_more: bool
    increase_facings: bool  # add more shelf space / product locations
    placement_suggestion: str
    reasoning: str
    source: str  # "claude" or "rule-based"


class CategoryStoreRecommendations(BaseModel):
    category: str
    recommendations: list[StoreRecommendation]


class StoreLocation(BaseModel):
    store_id: str
    city: str
    address: str
    state: str


class StoreLocationList(BaseModel):
    state: str
    stores: list[StoreLocation]
    simulated: bool  # always True today — see the note field on per-store endpoints


class StoreProductTrends(BaseModel):
    store_id: str
    category: str
    products: list[ProductTrend]
    note: str


class StoreLevelRecommendations(BaseModel):
    store_id: str
    category: str
    recommendations: list[StoreRecommendation]
    note: str


class ReportRecommendation(BaseModel):
    description: str
    total_sales: Optional[float] = None
    change_vs_ly_pct: Optional[float] = None
    regular_sales: Optional[float] = None
    expected_demand: str
    priority: str  # "high", "medium", "low"
    action: str
    order_more: bool
    increase_facings: bool
    placement_suggestion: str
    reasoning: str


class ReportAnalysisResult(BaseModel):
    item_count: int
    recommendations: list[ReportRecommendation]
    source: str  # "claude" (photo) or "rule-based" (CSV — exact numbers, no OCR needed)


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


class MaturedForecast(BaseModel):
    forecast_date: str
    predicted_units: float
    actual_units: float
    error_pct: float


class ForecastAccuracy(BaseModel):
    category: str
    matured: list[MaturedForecast]
    mape: Optional[float]
    pending_count: int


class Recommendation(BaseModel):
    category: str
    headline: str
    detail: str
    trend_change_pct: float
    forecast_change_pct: float
    source: str  # "claude" or "rule-based"


class WeatherDay(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_probability: float


class WeatherOutlook(BaseModel):
    location: str
    source: str  # "live" or "sample"
    days: list[WeatherDay]


class DashboardResponse(BaseModel):
    categories: list[CategoryInfo]
    recommendations: list[Recommendation]
