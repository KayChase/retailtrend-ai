import type {
  DashboardResponse,
  ForecastResult,
  RegionHeatMap,
  SeasonalPattern,
  TrendSeries,
} from "../types/api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  dashboard: () => getJson<DashboardResponse>("/api/dashboard"),
  trend: (category: string) => getJson<TrendSeries>(`/api/trends/${category}`),
  trendRegions: (category: string) => getJson<RegionHeatMap>(`/api/trends/${category}/regions`),
  forecast: (category: string) => getJson<ForecastResult>(`/api/forecast/${category}`),
  seasonal: (category: string) => getJson<SeasonalPattern>(`/api/forecast/${category}/seasonal`),
};
