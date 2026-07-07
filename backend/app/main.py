from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import categories, dashboard, data, forecast, recommendations, regions, reports, trends, weather
from app.services.data_loader import load_persisted_upload_on_startup

app = FastAPI(
    title="RetailTrend AI",
    description="Google Trends + sales forecasting + AI-generated merchandising recommendations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_persisted_upload_on_startup()

app.include_router(categories.router)
app.include_router(trends.router)
app.include_router(forecast.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)
app.include_router(data.router)
app.include_router(weather.router)
app.include_router(regions.router)
app.include_router(reports.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
