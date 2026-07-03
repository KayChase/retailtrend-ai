from fastapi import APIRouter, HTTPException

from app.config import CATEGORIES
from app.models.schemas import Recommendation
from app.services.ai_insights import generate_all_recommendations, generate_recommendation

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=list[Recommendation])
def list_recommendations() -> list[Recommendation]:
    return generate_all_recommendations()


@router.get("/{category}", response_model=Recommendation)
def get_recommendation(category: str) -> Recommendation:
    if category not in CATEGORIES:
        raise HTTPException(status_code=404, detail=f"Unknown category '{category}'")
    return generate_recommendation(category)
