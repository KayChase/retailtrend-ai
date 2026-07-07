import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { CategoryProductTrends } from "../types/api";

interface Props {
  category: string;
  categoryLabel: string;
}

export function TrendingList({ category, categoryLabel }: Props) {
  const [data, setData] = useState<CategoryProductTrends | null>(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    api.categoryProducts(category).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category]);

  if (!data) {
    return (
      <div className="card">
        <h2>Trending in {categoryLabel}</h2>
        <p className="muted">Loading...</p>
      </div>
    );
  }

  const sorted = [...data.products].sort((a, b) => b.change_pct - a.change_pct);
  const allLive = sorted.every((p) => p.source === "live");

  return (
    <div className="card">
      <div className="card-header">
        <h2>Trending in {categoryLabel}</h2>
        <span className="source-badge">{allLive ? "Live" : "Sample data"}</span>
      </div>
      <ul className="trending-list">
        {sorted.map((p) => (
          <li key={p.product} className="trending-row">
            <span className="trending-label">{p.product}</span>
            <span className={p.change_pct >= 0 ? "change-pct up" : "change-pct down"}>
              {p.change_pct >= 0 ? "+" : ""}
              {p.change_pct}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
