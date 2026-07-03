# RetailTrend AI

A retail demand-intelligence dashboard: Google Trends search interest, seasonal
pattern detection, Holt-Winters sales forecasting, regional heat maps, and
AI-generated merchandising recommendations for a set of seasonal drugstore
categories (allergy medicine, sunscreen, cold & flu, etc.).

## Architecture

- **Backend** (`backend/`) — FastAPI + pandas + statsmodels. Serves trend,
  forecast, and recommendation data over a REST API.
- **Frontend** (`frontend/`) — React + Vite + TypeScript + Recharts. Single-page
  dashboard that consumes the backend API.

### Data sources

- **Sales history** is synthetic: a deterministic (seeded) 36-month history per
  category x US state, generated on first run (`app/data/generate_sample_data.py`)
  and cached to `backend/app/data/sample_sales.csv`.
- **Google Trends** data comes from `pytrends` when reachable. Since Google
  Trends rate-limits aggressively and has no uptime guarantee, every trends call
  falls back to a deterministic synthetic series derived from sales seasonality
  if the live call fails. Every trend/region API response includes a `source`
  field (`"live"` or `"sample"`) so the UI can show which case occurred.
- **AI recommendations** call the Claude API (`claude-opus-4-7`) when
  `ANTHROPIC_API_KEY` is set, and fall back to deterministic rule-based text
  otherwise. Responses include a `source` field (`"claude"` or `"rule-based"`).

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optionally set ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # optionally change VITE_API_BASE_URL
npm run dev
```

By default the frontend expects the backend at `http://localhost:8000` and the
backend allows CORS from `http://localhost:5173`. If you run the frontend on a
different port, add it to `CORS_ORIGINS` in `backend/.env`.

## API

| Endpoint | Description |
| --- | --- |
| `GET /api/categories` | List of tracked product categories |
| `GET /api/trends/{category}` | 12-month Google Trends interest series |
| `GET /api/trends/{category}/regions` | Interest by US state |
| `GET /api/forecast/{category}` | Holt-Winters 3-month sales forecast |
| `GET /api/forecast/{category}/seasonal` | Monthly seasonality index |
| `GET /api/recommendations` | AI/rule-based recommendation per category |
| `GET /api/dashboard` | Aggregated payload for the dashboard UI |

## Notes

This is a standalone internal-tool prototype — it is not connected to any real
retailer's inventory, POS, or employee systems.
