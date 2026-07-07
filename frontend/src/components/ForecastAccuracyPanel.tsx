import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ForecastAccuracy } from "../types/api";

interface Props {
  category: string;
}

export function ForecastAccuracyPanel({ category }: Props) {
  const [data, setData] = useState<ForecastAccuracy | null>(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    api.forecastAccuracy(category).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category]);

  if (!data) {
    return (
      <div className="card">
        <h2>Forecast Accuracy</h2>
        <p className="muted">Loading...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>Forecast Accuracy</h2>
        {data.mape !== null && <span className="source-badge">MAPE: {data.mape}%</span>}
      </div>
      {data.matured.length === 0 ? (
        <p className="muted" style={{ fontSize: 13 }}>
          No forecasts have matured yet — a prediction can only be checked once its target month
          has actually passed. {data.pending_count} prediction{data.pending_count === 1 ? "" : "s"}{" "}
          {data.pending_count === 1 ? "is" : "are"} still pending.
        </p>
      ) : (
        <>
          <table className="accuracy-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Predicted</th>
                <th>Actual</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {data.matured.map((m) => (
                <tr key={m.forecast_date}>
                  <td>{m.forecast_date}</td>
                  <td>{m.predicted_units.toLocaleString()}</td>
                  <td>{m.actual_units.toLocaleString()}</td>
                  <td className={Math.abs(m.error_pct) <= 10 ? "change-pct up" : "change-pct down"}>
                    {m.error_pct >= 0 ? "+" : ""}
                    {m.error_pct}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.pending_count > 0 && (
            <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
              {data.pending_count} more prediction{data.pending_count === 1 ? "" : "s"} still pending.
            </p>
          )}
        </>
      )}
    </div>
  );
}
