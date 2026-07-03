from fastapi import APIRouter

from app.config import CATEGORIES
from app.models.schemas import CategoryInfo, DashboardResponse, TrendPoint, TrendSeries
from app.services.ai_insights import generate_all_recommendations
from app.services.google_trends import get_interest_over_time

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _change_pct(series) -> float:
    if series.empty or series.iloc[0] == 0:
        return 0.0
    return round((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100, 1)


@router.get("", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    categories = [
        CategoryInfo(key=key, label=key.replace("_", " ").title(), search_term=term)
        for key, term in CATEGORIES.items()
    ]

    trends = []
    for key, term in CATEGORIES.items():
        series, source = get_interest_over_time(term)
        points = [
            TrendPoint(date=str(d.date()) if hasattr(d, "date") else str(d), value=float(v))
            for d, v in series.items()
        ]
        trends.append(
            TrendSeries(
                category=key,
                search_term=term,
                change_pct=_change_pct(series),
                source=source,
                points=points,
            )
        )

    recommendations = generate_all_recommendations()

    return DashboardResponse(categories=categories, trends=trends, recommendations=recommendations)
