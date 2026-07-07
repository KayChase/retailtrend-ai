import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { CategoryStoreRecommendations } from "../types/api";

interface Props {
  category: string;
  categoryLabel: string;
  location: string;
}

export function StoreRecommendations({ category, categoryLabel, location }: Props) {
  const [data, setData] = useState<CategoryStoreRecommendations | null>(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    api.storeRecommendations(category, location).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category, location]);

  if (!data) {
    return (
      <div className="card">
        <h2>Store Recommendations</h2>
        <p className="muted">Loading...</p>
      </div>
    );
  }

  const sorted = [...data.recommendations].sort((a, b) => {
    const order = { high: 0, medium: 1, low: 2 };
    return order[a.priority] - order[b.priority];
  });
  const anyClaude = sorted.some((r) => r.source === "claude");

  return (
    <div className="card">
      <div className="card-header">
        <h2>Store Recommendations — {categoryLabel}</h2>
        <span className="source-badge">{anyClaude ? "Claude" : "Rule-based"}</span>
      </div>
      <div className="store-rec-list">
        {sorted.map((r) => (
          <div key={r.product} className={`store-rec-card priority-${r.priority}`}>
            <div className="store-rec-top">
              <span className="store-rec-product">{r.product}</span>
              <span className={`priority-pill priority-${r.priority}`}>{r.priority}</span>
            </div>
            <div className="store-rec-action">{r.action}</div>
            <div className="store-rec-tags">
              <span>Demand: {r.expected_demand}</span>
              <span>Trend: {r.trend_change_pct >= 0 ? "+" : ""}{r.trend_change_pct}%</span>
              {r.weather_boost_pct !== null && (
                <span>Weather: {r.weather_boost_pct >= 0 ? "+" : ""}{r.weather_boost_pct}%</span>
              )}
              <span>{r.order_more ? "Order more" : "No reorder"}</span>
              <span>{r.increase_facings ? "Expand shelf space" : "Keep shelf space"}</span>
            </div>
            <p className="store-rec-text">{r.placement_suggestion}</p>
            <p className="store-rec-text muted">{r.reasoning}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
