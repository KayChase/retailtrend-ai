import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api/client";
import type { SeasonalPattern } from "../types/api";

interface Props {
  category: string;
}

export function SeasonalChart({ category }: Props) {
  const [data, setData] = useState<SeasonalPattern | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.seasonal(category).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category]);

  if (!data) {
    return (
      <div className="card">
        <h2>Seasonal Pattern</h2>
        <p className="muted">Loading...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Seasonal Pattern</h2>
        <span className="source-badge">
          Peak: {data.peak_month} / Low: {data.low_month}
        </span>
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data.points}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2f3a" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="index" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
