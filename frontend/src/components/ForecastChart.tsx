import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api/client";
import type { ForecastResult } from "../types/api";

interface Props {
  category: string;
}

interface ChartRow {
  date: string;
  actual: number | null;
  forecast: number | null;
}

export function ForecastChart({ category }: Props) {
  const [data, setData] = useState<ForecastResult | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.forecast(category).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category]);

  if (!data) {
    return (
      <div className="card">
        <h2>Sales Forecast</h2>
        <p className="muted">Loading...</p>
      </div>
    );
  }

  const recentHistory = data.history.slice(-12);
  const rows: ChartRow[] = [
    ...recentHistory.map((p) => ({ date: p.date, actual: p.units, forecast: null })),
    ...data.forecast.map((p, i) => ({
      date: p.date,
      actual: i === 0 ? recentHistory[recentHistory.length - 1]?.units ?? null : null,
      forecast: p.units,
    })),
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h2>Sales Forecast</h2>
        <span className="source-badge">{data.method}</span>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e8e2e2" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="actual" name="Actual" stroke="#cc0000" dot={false} connectNulls />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke="#1a1a1a"
            strokeDasharray="5 5"
            dot={false}
            connectNulls
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
