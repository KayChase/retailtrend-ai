from fastapi import APIRouter

from app.config import CATEGORIES, CATEGORY_LABELS
from app.models.schemas import CategoryInfo, DashboardResponse
from app.services.ai_insights import generate_all_recommendations

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    categories = [
        CategoryInfo(key=key, label=CATEGORY_LABELS[key], search_term=term)
        for key, term in CATEGORIES.items()
    ]

    recommendations = generate_all_recommendations()

    return DashboardResponse(categories=categories, recommendations=recommendations)
