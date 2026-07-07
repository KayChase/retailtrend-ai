import type {
  CategoryProductTrends,
  CategoryStoreRecommendations,
  DashboardResponse,
  DataStatus,
  DataUploadResult,
  ForecastAccuracy,
  ForecastResult,
  RegionHeatMap,
  ReportAnalysisResult,
  SeasonalPattern,
  StoreLevelRecommendations,
  StoreLocationList,
  StoreProductTrends,
  TrendSeries,
  WeatherOutlook,
} from "../types/api";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

async function postJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "POST", ...options });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request to ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  dashboard: () => getJson<DashboardResponse>("/api/dashboard"),
  trend: (category: string) => getJson<TrendSeries>(`/api/trends/${category}`),
  trendRegions: (category: string) => getJson<RegionHeatMap>(`/api/trends/${category}/regions`),
  categoryProducts: (category: string) =>
    getJson<CategoryProductTrends>(`/api/trends/${category}/products`),
  forecast: (category: string) => getJson<ForecastResult>(`/api/forecast/${category}`),
  seasonal: (category: string) => getJson<SeasonalPattern>(`/api/forecast/${category}/seasonal`),
  forecastAccuracy: (category: string) =>
    getJson<ForecastAccuracy>(`/api/forecast/${category}/accuracy`),
  storeRecommendations: (category: string, location?: string) =>
    getJson<CategoryStoreRecommendations>(
      `/api/recommendations/${category}/products${location ? `?location=${encodeURIComponent(location)}` : ""}`
    ),
  weather: (location?: string) =>
    getJson<WeatherOutlook>(`/api/weather${location ? `?location=${encodeURIComponent(location)}` : ""}`),
  dataStatus: () => getJson<DataStatus>("/api/data/status"),
  regionStores: (state: string) => getJson<StoreLocationList>(`/api/regions/${state}/stores`),
  storeProductTrends: (state: string, storeId: string, category: string) =>
    getJson<StoreProductTrends>(
      `/api/regions/${state}/stores/${storeId}/products?category=${encodeURIComponent(category)}`
    ),
  storeRecommendationsAt: (state: string, storeId: string, category: string, location?: string) =>
    getJson<StoreLevelRecommendations>(
      `/api/regions/${state}/stores/${storeId}/recommendations?category=${encodeURIComponent(category)}` +
        (location ? `&location=${encodeURIComponent(location)}` : "")
    ),
  uploadData: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return postJson<DataUploadResult>("/api/data/upload", { body: formData });
  },
  resetData: () => postJson<DataStatus>("/api/data/reset"),
  analyzeReportImage: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return postJson<ReportAnalysisResult>("/api/reports/analyze", { body: formData });
  },
  analyzeReportCsv: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return postJson<ReportAnalysisResult>("/api/reports/analyze-csv", { body: formData });
  },
};
