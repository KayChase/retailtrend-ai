import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_SALES_CSV = DATA_DIR / "sample_sales.csv"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

# Retail categories tracked across the whole app. Keep the Google Trends
# search term and the internal sales-data category key in sync here.
CATEGORIES = {
    "allergy_medicine": "allergy medicine",
    "bug_spray": "bug spray",
    "melatonin": "melatonin",
    "vitamin_d": "vitamin d",
    "sunscreen": "sunscreen",
    "cold_flu": "cold and flu medicine",
    "cough_drops": "cough drops",
    "hand_sanitizer": "hand sanitizer",
}

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]
