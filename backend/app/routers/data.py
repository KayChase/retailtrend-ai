import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services import (
    data_loader,
    forecast_accuracy,
    google_trends,
    product_trends,
    store_recommendations,
)

router = APIRouter(prefix="/api/data", tags=["data"])


def _clear_derived_caches() -> None:
    google_trends.clear_cache()
    product_trends.clear_cache()
    store_recommendations.clear_cache()
    forecast_accuracy.clear_log()


@router.get("/status")
def get_status() -> dict:
    return data_loader.data_status()


@router.post("/upload")
async def upload_sales_data(file: UploadFile = File(...)) -> dict:
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    try:
        df = pd.read_csv(file.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded file has no rows.")

    try:
        warnings = data_loader.validate_sales_csv(df)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    data_loader.set_uploaded_data(df)
    _clear_derived_caches()

    return {**data_loader.data_status(), "warnings": warnings}


@router.post("/reset")
def reset_to_sample_data() -> dict:
    data_loader.clear_uploaded_data()
    _clear_derived_caches()
    return data_loader.data_status()
