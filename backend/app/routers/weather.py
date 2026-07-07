from typing import Optional

from fastapi import APIRouter, Query

from app.models.schemas import WeatherDay, WeatherOutlook
from app.services.weather import get_weather_outlook

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("", response_model=WeatherOutlook)
def get_weather(location: Optional[str] = Query(default=None)) -> WeatherOutlook:
    result = get_weather_outlook(location)
    return WeatherOutlook(
        location=result["location"],
        source=result["source"],
        days=[WeatherDay(**d) for d in result["days"]],
    )
