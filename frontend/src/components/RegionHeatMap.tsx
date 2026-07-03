import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { RegionHeatMap as RegionHeatMapData } from "../types/api";

interface Props {
  category: string;
}

function colorFor(value: number, max: number): string {
  const intensity = max ? value / max : 0;
  const alpha = 0.15 + intensity * 0.75;
  return `rgba(37, 99, 235, ${alpha.toFixed(2)})`;
}

export function RegionHeatMap({ category }: Props) {
  const [data, setData] = useState<RegionHeatMapData | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.trendRegions(category).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category]);

  if (!data) {
    return (
      <div className="card">
        <h2>Regional Interest</h2>
        <p className="muted">Loading...</p>
      </div>
    );
  }

  const max = Math.max(...data.regions.map((r) => r.value), 1);

  return (
    <div className="card">
      <div className="card-header">
        <h2>Regional Interest</h2>
        <span className="source-badge">{data.source === "live" ? "Live" : "Sample data"}</span>
      </div>
      <div className="heatmap-grid">
        {data.regions.map((r) => (
          <div
            key={r.region}
            className="heatmap-cell"
            style={{ backgroundColor: colorFor(r.value, max) }}
            title={`${r.region}: ${r.value}`}
          >
            <span className="heatmap-region">{r.region}</span>
            <span className="heatmap-value">{r.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
