import { useEffect, useState } from "react";
import { api } from "./api/client";
import { CategorySelector } from "./components/CategorySelector";
import { DataUpload } from "./components/DataUpload";
import { ForecastAccuracyPanel } from "./components/ForecastAccuracyPanel";
import { ForecastChart } from "./components/ForecastChart";
import { RecommendationPanel } from "./components/RecommendationPanel";
import { RegionHeatMap } from "./components/RegionHeatMap";
import { ReportImageUpload } from "./components/ReportImageUpload";
import { SeasonalChart } from "./components/SeasonalChart";
import { StoreRecommendations } from "./components/StoreRecommendations";
import { TrendingList } from "./components/TrendingList";
import { WeatherOutlook } from "./components/WeatherOutlook";
import type { DashboardResponse } from "./types/api";
import "./App.css";

function App() {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [selected, setSelected] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [location, setLocation] = useState("New York, NY");
  const [dataVersion, setDataVersion] = useState(0);

  const loadDashboard = () => {
    api
      .dashboard()
      .then((res) => {
        setDashboard(res);
        setSelected((current) => current || res.categories[0]?.key || "");
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  };

  useEffect(loadDashboard, []);

  const handleDataChanged = () => {
    setDataVersion((v) => v + 1);
    loadDashboard();
  };

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
  const selectedLabel = dashboard.categories.find((c) => c.key === selected)?.label ?? selected;

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-row">
          <svg className="heart-logo" viewBox="0 0 24 24" aria-hidden="true">
            <path
              fill="currentColor"
              d="M12 21s-6.7-4.35-9.3-8.28C1 10.5 1 7 3.6 5.4 5.9 4 8.6 4.7 10 7c.4-.6.9-1.1 1.4-1.5C13.9 3.9 17 4 19.1 6.4c1.9 2.1 1.6 5.1-.2 7.3C15.3 17.6 12 21 12 21z"
            />
          </svg>
          <div>
            <h1>RetailTrend AI</h1>
            <p className="slogan">"Health is everything."</p>
          </div>
        </div>
        <p className="muted">Search trends, demand forecasting, and merchandising recommendations</p>
        <p className="disclaimer">
          Independent portfolio project styled after CVS Health's brand colors. Not affiliated
          with, endorsed by, or produced by CVS Health.
        </p>
      </header>

      <CategorySelector
        categories={dashboard.categories}
        selected={selected}
        onSelect={setSelected}
      />

      <div key={dataVersion}>
        <div className="dashboard-grid">
          <div className="dashboard-col">
            <TrendingList category={selected} categoryLabel={selectedLabel} />
            <RecommendationPanel recommendation={recommendation} />
            <WeatherOutlook location={location} onLocationChange={setLocation} />
          </div>
          <div className="dashboard-col dashboard-col-wide">
            <ForecastChart category={selected} />
            <ForecastAccuracyPanel category={selected} />
            <SeasonalChart category={selected} />
            <RegionHeatMap category={selected} location={location} />
          </div>
        </div>

        <div className="full-width-section">
          <StoreRecommendations category={selected} categoryLabel={selectedLabel} location={location} />
        </div>
      </div>

      <div className="full-width-section">
        <ReportImageUpload />
      </div>

      <div className="full-width-section">
        <DataUpload onDataChanged={handleDataChanged} />
      </div>
    </div>
  );
}

export default App;
