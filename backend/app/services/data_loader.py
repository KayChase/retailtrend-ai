from functools import lru_cache

import pandas as pd

from app.config import SAMPLE_SALES_CSV
from app.data.generate_sample_data import generate


@lru_cache(maxsize=1)
def load_sales_data() -> pd.DataFrame:
    """Loads the synthetic sales history, generating it on first run."""
    if not SAMPLE_SALES_CSV.exists():
        df = generate()
        SAMPLE_SALES_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(SAMPLE_SALES_CSV, index=False)
    else:
        df = pd.read_csv(SAMPLE_SALES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    return df


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
