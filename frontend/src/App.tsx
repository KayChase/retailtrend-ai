import { useEffect, useState } from "react";
import { api } from "./api/client";
import { CategorySelector } from "./components/CategorySelector";
import { ForecastChart } from "./components/ForecastChart";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { RegionHeatMap } from "./components/RegionHeatMap";
import { SeasonalChart } from "./components/SeasonalChart";
import { TrendingList } from "./components/TrendingList";
import type { DashboardResponse } from "./types/api";
import "./App.css";

function App() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [selected, setSelected] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .dashboard()
      .then((res) => {
        setDashboard(res);
        setSelected(res.categories[0]?.key ?? "");
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  if (error) {
    return (
      <div className="app-shell">
        <p className="error-banner">
          Could not reach the backend at the configured API URL. Is the FastAPI server running?
          <br />
          {error}
        </p>
      </div>
    );
  }

  if (!dashboard || !selected) {
    return (
      <div className="app-shell">
        <p className="muted">Loading dashboard...</p>
      </div>
    );
  }

  const recommendation = dashboard.recommendations.find((r) => r.category === selected);

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>RetailTrend AI</h1>
        <p className="muted">Search trends, demand forecasting, and merchandising recommendations</p>
      </header>

      <CategorySelector
        categories={dashboard.categories}
        selected={selected}
        onSelect={setSelected}
      />

      <div className="dashboard-grid">
        <div className="dashboard-col">
          <TrendingList trends={dashboard.trends} selected={selected} onSelect={setSelected} />
          <RecommendationPanel recommendation={recommendation} />
        </div>
        <div className="dashboard-col dashboard-col-wide">
          <ForecastChart category={selected} />
          <SeasonalChart category={selected} />
          <RegionHeatMap category={selected} />
        </div>
      </div>
    </div>
  );
}

export default App;
