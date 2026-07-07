import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schemas import ReportAnalysisResult, ReportRecommendation
from app.services.report_analysis import analyze_report_csv
from app.services.report_vision import analyze_report_image

router = APIRouter(prefix="/api/reports", tags=["reports"])

ALLOWED_MEDIA_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 15 * 1024 * 1024  # 15MB


@router.post("/analyze", response_model=ReportAnalysisResult)
async def analyze_report(file: UploadFile = File(...)) -> ReportAnalysisResult:
    media_type = file.content_type or ""
    if media_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPEG, PNG, WebP, or GIF photo of the report.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image is too large (max 15MB).")

    try:
        items = analyze_report_image(image_bytes, media_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ReportAnalysisResult(
        item_count=len(items),
        recommendations=[ReportRecommendation(**item) for item in items],
        source="claude",
    )


@router.post("/analyze-csv", response_model=ReportAnalysisResult)
async def analyze_report_csv_upload(file: UploadFile = File(...)) -> ReportAnalysisResult:
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    try:
        df = pd.read_csv(file.file)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="The uploaded file has no rows.")

    try:
        items = analyze_report_csv(df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ReportAnalysisResult(
        item_count=len(items),
        recommendations=[ReportRecommendation(**item) for item in items],
        source="rule-based",
    )
