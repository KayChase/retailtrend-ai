"""
Loads the sales history the rest of the app runs on. Defaults to synthetic
sample data; if the user uploads a real sales CSV (see app/routers/data.py),
that takes over instead, and persists to disk so it survives a backend
restart. Everything downstream (forecasting, seasonal patterns, region
snapshots) reads through load_sales_data() and doesn't need to know which
source is active.
"""
from typing import Optional

import pandas as pd

from app.config import CATEGORIES, SAMPLE_SALES_CSV, UPLOADED_SALES_CSV
from app.data.generate_sample_data import generate

REQUIRED_COLUMNS = {"date", "category", "units_sold"}
NO_REGION_PLACEHOLDER = "All Regions"

_sample_cache: Optional[pd.DataFrame] = None
_uploaded_df: Optional[pd.DataFrame] = None


def _load_sample_data() -> pd.DataFrame:
    global _sample_cache
    if _sample_cache is not None:
        return _sample_cache

    if not SAMPLE_SALES_CSV.exists():
        df = generate()
        SAMPLE_SALES_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(SAMPLE_SALES_CSV, index=False)
    else:
        df = pd.read_csv(SAMPLE_SALES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    _sample_cache = df
    return df


def load_sales_data() -> pd.DataFrame:
    if _uploaded_df is not None:
        return _uploaded_df
    return _load_sample_data()


def is_using_uploaded_data() -> bool:
    return _uploaded_df is not None


def validate_sales_csv(df: pd.DataFrame) -> list[str]:
    """Returns a list of human-readable warnings; empty means it's usable as-is."""
    warnings = []
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

    if "region" not in df.columns:
        warnings.append(
            "No 'region' column found — regional heat maps will show a single "
            f"'{NO_REGION_PLACEHOLDER}' bucket instead of per-state breakdowns."
        )

    unknown_categories = sorted(set(df["category"]) - set(CATEGORIES.keys()))
    if unknown_categories:
        warnings.append(
            "These category values don't match any known department and won't be "
            f"reachable in the dashboard: {', '.join(unknown_categories)}. Expected one "
            f"of: {', '.join(CATEGORIES.keys())}."
        )

    if not pd.to_numeric(df["units_sold"], errors="coerce").notna().all():
        raise ValueError("'units_sold' column contains non-numeric values.")

    dates_per_category = df.groupby("category")["date"].nunique()
    if not dates_per_category.empty and dates_per_category.max() > 60:
        warnings.append(
            "Some categories have more than 60 distinct dates, which suggests daily "
            "(not monthly) data. Forecasting and seasonal patterns assume one row per "
            "month per category/region — consider pre-aggregating to monthly totals "
            "for meaningful results."
        )

    return warnings


def set_uploaded_data(df: pd.DataFrame) -> None:
    global _uploaded_df

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["units_sold"] = pd.to_numeric(df["units_sold"])
    if "region" not in df.columns:
        df["region"] = NO_REGION_PLACEHOLDER

    _uploaded_df = df
    UPLOADED_SALES_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(UPLOADED_SALES_CSV, index=False)


def clear_uploaded_data() -> None:
    global _uploaded_df
    _uploaded_df = None
    if UPLOADED_SALES_CSV.exists():
        UPLOADED_SALES_CSV.unlink()


def load_persisted_upload_on_startup() -> None:
    """Restores a previously-uploaded dataset after a backend restart."""
    global _uploaded_df
    if UPLOADED_SALES_CSV.exists():
        df = pd.read_csv(UPLOADED_SALES_CSV)
        df["date"] = pd.to_datetime(df["date"])
        _uploaded_df = df


def data_status() -> dict:
    df = load_sales_data()
    return {
        "using_uploaded_data": is_using_uploaded_data(),
        "rows": int(len(df)),
        "date_range": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
        },
        "categories": sorted(str(c) for c in df["category"].unique()),
        "has_region_data": bool((df["region"] != NO_REGION_PLACEHOLDER).any()) if "region" in df.columns else False,
    }


def category_series(category: str) -> pd.Series:
    """Monthly total units sold across all regions for one category."""
    df = load_sales_data()
    cat_df = df[df["category"] == category]
    monthly = cat_df.groupby("date")["units_sold"].sum().sort_index()
    return monthly


def category_region_snapshot(category: str) -> pd.DataFrame:
    """Latest month's units sold per region for one category."""
    df = load_sales_data()
    cat_df = df[df["category"] == category]
    latest_date = cat_df["date"].max()
    snapshot = cat_df[cat_df["date"] == latest_date]
    return snapshot[["region", "units_sold"]].sort_values("units_sold", ascending=False)
