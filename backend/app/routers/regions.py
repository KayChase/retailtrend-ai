from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import CATEGORIES
from app.models.schemas import (
    ProductTrend,
    StoreLevelRecommendations,
    StoreLocation,
    StoreLocationList,
    StoreProductTrends,
)
from app.services.store_locations import get_store_product_trends, get_store_recommendations, list_stores

router = APIRouter(prefix="/api/regions", tags=["regions"])

SIMULATED_NOTE = "Simulated store-level data on top of the category-level trend — not a real store's actual sales."


@router.get("/{state}/stores", response_model=StoreLocationList)
def get_stores(state: str) -> StoreLocationList:
    stores = list_stores(state)
    return StoreLocationList(
        state=state.upper(),
        stores=[StoreLocation(**s, state=state.upper()) for s in stores],
        simulated=True,
    )


@router.get("/{state}/stores/{store_id}/products", response_model=StoreProductTrends)
def get_store_products(state: str, store_id: str, category: str = Query(...)) -> StoreProductTrends:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    try:
        products = get_store_product_trends(state, store_id, category)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return StoreProductTrends(
        store_id=store_id,
        category=category,
        products=[ProductTrend(**p) for p in products],
        note=SIMULATED_NOTE,
    )


@router.get("/{state}/stores/{store_id}/recommendations", response_model=StoreLevelRecommendations)
def get_store_recs(
    state: str,
    store_id: str,
    category: str = Query(...),
    location: Optional[str] = Query(default=None),
) -> StoreLevelRecommendations:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    try:
        recommendations = get_store_recommendations(state, store_id, category, location)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return StoreLevelRecommendations(
        store_id=store_id,
        category=category,
        recommendations=recommendations,
        note=SIMULATED_NOTE,
    )
