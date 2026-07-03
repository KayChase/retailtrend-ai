from fastapi import APIRouter

from app.config import CATEGORIES
from app.models.schemas import CategoryInfo

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryInfo])
def list_categories() -> list[CategoryInfo]:
    return [
        CategoryInfo(key=key, label=key.replace("_", " ").title(), search_term=term)
        for key, term in CATEGORIES.items()
    ]
