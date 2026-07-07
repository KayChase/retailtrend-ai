"""
Reads a photo of a printed store sales report (SKU, description, total sales,
% vs last year, regular sales — the exact columns a store's POS system
prints) and turns it directly into per-item store recommendations. This has
no non-LLM fallback: OCR-ing a skewed, cropped phone photo and reasoning
about each row is squarely a vision+reasoning task, so it requires
ANTHROPIC_API_KEY to be configured.
"""
import base64
import json
from typing import Optional

import anthropic

from app.config import ANTHROPIC_API_KEY

MODEL = "claude-opus-4-8"

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

PROMPT = (
    "You are a retail merchandising analyst. The attached photo is a printed sales "
    "report from a store's POS system. It typically has columns like SKU, item "
    "description, total sales amount, percent change vs last year (\"vs LY\"), and "
    "regular (non-promotional) sales amount — but the exact columns, and how much of "
    "the photo is in focus or cropped, can vary. Read every row you can make out.\n\n"
    "For each row, produce a store operations recommendation:\n"
    "- If a 'vs LY' or similar year-over-year percent is visible, use it as the trend "
    "signal (>= 40% or a big jump: high priority, increase stock and shelf space; "
    "15-40%: order more; roughly flat: maintain; -15% to -40%: reduce future orders; "
    "worse than that: reduce stock and reconsider placement).\n"
    "- If no percent is legible for a row, use the sales amount and your judgement "
    "of the item's likely trend to give a qualitative recommendation instead of "
    "leaving it blank.\n\n"
    "Respond with ONLY a JSON array (no markdown fences, no prose before or after), one "
    "object per row you can read, with exactly these fields: "
    '"description" (the item name/description as printed), "total_sales" (number, no '
    "$ sign, or null if not visible), \"change_vs_ly_pct\" (number, e.g. 45.4 for "
    "\"45.4%\", or null if not visible/legible), \"regular_sales\" (number or null), "
    '"expected_demand" (short phrase like "Rising sharply", "Stable", "Declining"), '
    '"priority" ("high", "medium", or "low"), "action" (short label, max 6 words), '
    '"order_more" (boolean), "increase_facings" (boolean, whether to give the item more '
    'shelf space/locations), "placement_suggestion" (one sentence), and "reasoning" (one '
    "sentence explaining the recommendation using whatever data from the photo you used)."
)


def _parse_json_array(text: str) -> Optional[list[dict]]:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, list) else None


def analyze_report_image(image_bytes: bytes, media_type: str) -> list[dict]:
    if _client is None:
        raise ValueError(
            "Image report analysis requires ANTHROPIC_API_KEY to be configured "
            "— there's no non-AI fallback for reading a photo."
        )

    encoded = base64.standard_b64encode(image_bytes).decode("utf-8")

    response = _client.messages.create(
        model=MODEL,
        max_tokens=8000,
        thinking={"type": "adaptive"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": encoded,
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )

    text = "".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        raise ValueError("Claude returned no readable output for this image.")

    parsed = _parse_json_array(text)
    if parsed is None:
        raise ValueError("Could not parse a recommendation list from Claude's response.")

    results = []
    for item in parsed:
        if "description" not in item:
            continue
        results.append(
            {
                "description": str(item["description"]),
                "total_sales": item.get("total_sales"),
                "change_vs_ly_pct": item.get("change_vs_ly_pct"),
                "regular_sales": item.get("regular_sales"),
                "expected_demand": str(item.get("expected_demand", "Unknown")),
                "priority": str(item.get("priority", "low")),
                "action": str(item.get("action", "Maintain Current Stock")),
                "order_more": bool(item.get("order_more", False)),
                "increase_facings": bool(item.get("increase_facings", False)),
                "placement_suggestion": str(item.get("placement_suggestion", "")),
                "reasoning": str(item.get("reasoning", "")),
            }
        )

    if not results:
        raise ValueError("No readable rows were found in this image.")

    return results
