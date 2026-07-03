import type { Recommendation } from "../types/api";

interface Props {
  recommendation?: Recommendation;
}

export function RecommendationPanel({ recommendation }: Props) {
  if (!recommendation) {
    return null;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2>AI Recommendation</h2>
        <span className="source-badge">
          {recommendation.source === "claude" ? "Claude" : "Rule-based"}
        </span>
      </div>
      <h3 className="recommendation-headline">{recommendation.headline}</h3>
      <p className="recommendation-detail">{recommendation.detail}</p>
      <div className="recommendation-stats">
        <span>Search trend: {recommendation.trend_change_pct}%</span>
        <span>Forecast: {recommendation.forecast_change_pct}%</span>
      </div>
    </div>
  );
}
