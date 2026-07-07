"""
Parses a CSV export of a printed store sales report — SKU, SKU Description,
Total Sales Amount, % vs Last Year, Regular Sales Amount — the same fields
report_vision.py reads off a photo of that report. Unlike the photo path,
a CSV gives exact numbers with no OCR involved, so recommendations here are
computed with the same deterministic thresholds used elsewhere in the app
(see app/services/store_recommendations.py) and need no Claude API call.
"""
from typing import Optional

import pandas as pd

REQUIRED_HINT = (
    "Expected columns: a description column (e.g. 'SKU Description'), a total "
    "sales amount column, a percent-vs-last-year column, and optionally a "
    "regular sales amount column and a SKU column."
)


def _find_column(columns: list[str], keywords: list[str]) -> Optional[str]:
    normalized = {c: c.strip().lower() for c in columns}
    for keyword in keywords:
        for original, norm in normalized.items():
            if keyword in norm:
                return original
    return None


def _to_float(value) -> Optional[float]:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").replace("%", "").strip()
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_report_csv(df: pd.DataFrame) -> list[dict]:
    """Returns [{description, total_sales, change_vs_ly_pct, regular_sales}]."""
    columns = list(df.columns)

    description_col = _find_column(columns, ["sku description", "description", "item"])
    if description_col is None:
        description_col = _find_column(columns, ["sku"])
    if description_col is None:
        raise ValueError(f"Could not find a description column. {REQUIRED_HINT}")

    ly_col = _find_column(columns, ["vs ly", "vs. ly", "vs last year", "change vs ly", "yoy"])

    amount_cols = [c for c in columns if "amount" in c.strip().lower()] or [
        c for c in columns if "sales" in c.strip().lower()
    ]
    total_sales_col = _find_column(columns, ["total sales"]) or (amount_cols[0] if amount_cols else None)
    regular_sales_col = _find_column(columns, ["regular sales"])
    if regular_sales_col is None and len(amount_cols) > 1:
        regular_sales_col = amount_cols[1]

    if total_sales_col is None and ly_col is None:
        raise ValueError(f"Could not find a sales amount or vs-LY column. {REQUIRED_HINT}")

    rows = []
    for _, row in df.iterrows():
        description = row.get(description_col)
        if pd.isna(description) or not str(description).strip():
            continue
        rows.append(
            {
                "description": str(description).strip(),
                "total_sales": _to_float(row.get(total_sales_col)) if total_sales_col else None,
                "change_vs_ly_pct": _to_float(row.get(ly_col)) if ly_col else None,
                "regular_sales": _to_float(row.get(regular_sales_col)) if regular_sales_col else None,
            }
        )

    if not rows:
        raise ValueError("No usable rows found in this CSV.")

    return rows


def _rule_based_item(description: str, change_vs_ly_pct: Optional[float]) -> dict:
    if change_vs_ly_pct is None:
        return {
            "expected_demand": "Unknown",
            "priority": "low",
            "action": "Review Manually",
            "order_more": False,
            "increase_facings": False,
            "placement_suggestion": "No placement change until this item's trend can be confirmed.",
            "reasoning": f"No 'vs last year' figure was available for {description} in this report.",
        }

    pct = change_vs_ly_pct
    if pct >= 40:
        priority, action = "high", "Increase Stock & Expand Placement"
        demand, order_more, increase_facings = "Rising sharply", True, True
        placement = "Move to an endcap or eye-level shelf to capture the surge in demand."
    elif pct >= 15:
        priority, action = "medium", "Order More"
        demand, order_more, increase_facings = "Rising", True, False
        placement = "Keep current placement, but consider a secondary display near checkout."
    elif pct > -15:
        priority, action = "low", "Maintain Current Stock"
        demand, order_more, increase_facings = "Stable", False, False
        placement = "No placement changes needed right now."
    elif pct > -40:
        priority, action = "medium", "Reduce Future Orders"
        demand, order_more, increase_facings = "Declining", False, False
        placement = "Consolidate facings to free up space for trending items."
    else:
        priority, action = "high", "Reduce Stock & Reconsider Placement"
        demand, order_more, increase_facings = "Declining sharply", False, False
        placement = "Move to a less prominent shelf position or a clearance display."

    reasoning = (
        f"{description} is {'up' if pct >= 0 else 'down'} {abs(pct)}% vs last year, "
        f"which points to {demand.lower()} demand."
    )

    return {
        "expected_demand": demand,
        "priority": priority,
        "action": action,
        "order_more": order_more,
        "increase_facings": increase_facings,
        "placement_suggestion": placement,
        "reasoning": reasoning,
    }


def analyze_report_csv(df: pd.DataFrame) -> list[dict]:
    rows = parse_report_csv(df)
    results = []
    for row in rows:
        fields = _rule_based_item(row["description"], row["change_vs_ly_pct"])
        results.append({**row, **fields})
    return results
