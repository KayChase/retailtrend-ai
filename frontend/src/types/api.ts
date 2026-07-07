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

export interface ProductTrend {
  product: string;
  change_pct: number;
  source: "live" | "sample";
}

export interface CategoryProductTrends {
  category: string;
  products: ProductTrend[];
}

export interface StoreRecommendation {
  product: string;
  trend_change_pct: number;
  weather_boost_pct: number | null;
  expected_demand: string;
  priority: "high" | "medium" | "low";
  action: string;
  order_more: boolean;
  increase_facings: boolean;
  placement_suggestion: string;
  reasoning: string;
  source: "claude" | "rule-based";
}

export interface CategoryStoreRecommendations {
  category: string;
  recommendations: StoreRecommendation[];
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
  recommendations: Recommendation[];
}

export interface WeatherDay {
  date: string;
  temp_max: number;
  temp_min: number;
  precipitation_probability: number;
}

export interface WeatherOutlook {
  location: string;
  source: "live" | "sample";
  days: WeatherDay[];
}

export interface MaturedForecast {
  forecast_date: string;
  predicted_units: number;
  actual_units: number;
  error_pct: number;
}

export interface ForecastAccuracy {
  category: string;
  matured: MaturedForecast[];
  mape: number | null;
  pending_count: number;
}

export interface DataStatus {
  using_uploaded_data: boolean;
  rows: number;
  date_range: { start: string; end: string };
  categories: string[];
  has_region_data: boolean;
}

export interface DataUploadResult extends DataStatus {
  warnings: string[];
}

export interface StoreLocation {
  store_id: string;
  city: string;
  address: string;
  state: string;
}

export interface StoreLocationList {
  state: string;
  stores: StoreLocation[];
  simulated: boolean;
}

export interface StoreProductTrends {
  store_id: string;
  category: string;
  products: ProductTrend[];
  note: string;
}

export interface StoreLevelRecommendations {
  store_id: string;
  category: string;
  recommendations: StoreRecommendation[];
  note: string;
}

export interface ReportRecommendation {
  description: string;
  total_sales: number | null;
  change_vs_ly_pct: number | null;
  regular_sales: number | null;
  expected_demand: string;
  priority: "high" | "medium" | "low";
  action: string;
  order_more: boolean;
  increase_facings: boolean;
  placement_suggestion: string;
  reasoning: string;
}

export interface ReportAnalysisResult {
  item_count: number;
  recommendations: ReportRecommendation[];
  source: "claude";
}
