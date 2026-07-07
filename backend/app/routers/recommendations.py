from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.config import CATEGORIES
from app.models.schemas import CategoryStoreRecommendations, Recommendation
from app.services.ai_insights import generate_all_recommendations, generate_recommendation
from app.services.store_recommendations import get_store_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=list[Recommendation])
def list_recommendations() -> list[Recommendation]:
    return generate_all_recommendations()


@router.get("/{category}", response_model=Recommendation)
def get_recommendation(category: str) -> Recommendation:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    return generate_recommendation(category)


@router.get("/{category}/products", response_model=CategoryStoreRecommendations)
def get_product_store_recommendations(
    category: str, location: Optional[str] = Query(default=None)
) -> CategoryStoreRecommendations:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    return CategoryStoreRecommendations(
        category=category,
        recommendations=get_store_recommendations(category, location),
    )
