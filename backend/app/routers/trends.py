from fastapi import APIRouter, HTTPException

from app.config import CATEGORIES
from app.models.schemas import (
    CategoryProductTrends,
    ProductTrend,
    RegionHeatMap,
    RegionValue,
    TrendPoint,
    TrendSeries,
)
from app.services.google_trends import get_interest_by_region, get_interest_over_time
from app.services.product_trends import get_product_trends

router = APIRouter(prefix="/api/trends", tags=["trends"])


def _change_pct(series) -> float:
    if series.empty or series.iloc[0] == 0:
        return 0.0
    return round((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100, 1)


@router.get("/{category}", response_model=TrendSeries)
def get_trend(category: str) -> TrendSeries:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")

    search_term = CATEGORIES[category]
    series, source = get_interest_over_time(search_term)
    points = [TrendPoint(date=str(d.date()) if hasattr(d, "date") else str(d), value=float(v)) for d, v in series.items()]

    return TrendSeries(
        category=category,
        search_term=search_term,
        change_pct=_change_pct(series),
        source=source,
        points=points,
    )


@router.get("/{category}/products", response_model=CategoryProductTrends)
def get_category_products(category: str) -> CategoryProductTrends:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")

    products = get_product_trends(category)
    return CategoryProductTrends(
        category=category,
        products=[ProductTrend(**p) for p in products],
    )


@router.get("/{category}/regions", response_model=RegionHeatMap)
def get_trend_regions(category: str) -> RegionHeatMap:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")

    search_term = CATEGORIES[category]
    series, source = get_interest_by_region(search_term)
    regions = [RegionValue(region=str(r), value=float(v)) for r, v in series.items()]
    regions.sort(key=lambda r: r.value, reverse=True)

    return RegionHeatMap(category=category, source=source, regions=regions)
