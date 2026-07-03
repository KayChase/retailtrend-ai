export interface CategoryInfo {
  key: string;
  label: string;
  search_term: string;
}

export interface TrendPoint {
  date: string;
  value: number;
}

export interface TrendSeries {
  category: string;
  search_term: string;
  change_pct: number;
  source: "live" | "sample";
  points: TrendPoint[];
}

export interface RegionValue {
  region: string;
  value: number;
}

export interface RegionHeatMap {
  category: string;
  source: "live" | "sample";
  regions: RegionValue[];
}

export interface SeasonalPoint {
  month: string;
  avg_units: number;
  index: number;
}

export interface SeasonalPattern {
  category: string;
  peak_month: string;
  low_month: string;
  points: SeasonalPoint[];
}

export interface ForecastPoint {
  date: string;
  units: number;
  is_forecast: boolean;
}

export interface ForecastResult {
  category: string;
  method: string;
  history: ForecastPoint[];
  forecast: ForecastPoint[];
}

export interface Recommendation {
  category: string;
  headline: string;
  detail: string;
  trend_change_pct: number;
  forecast_change_pct: number;
  source: "claude" | "rule-based";
}

export interface DashboardResponse {
  categories: CategoryInfo[];
  trends: TrendSeries[];
  recommendations: Recommendation[];
}
