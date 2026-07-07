import { useEffect, useState } from "react";
import { api } from "../api/client";
import type {
  RegionHeatMap as RegionHeatMapData,
  StoreLevelRecommendations,
  StoreLocation,
  StoreProductTrends,
} from "../types/api";

interface Props {
  category: string;
  location: string;
}

function colorFor(value: number, max: number): string {
  const intensity = max ? value / max : 0;
  const alpha = 0.15 + intensity * 0.75;
  return `rgba(204, 0, 0, ${alpha.toFixed(2)})`;
}

export function RegionHeatMap({ category, location }: Props) {
  const [data, setData] = useState<RegionHeatMapData | null>(null);
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [stores, setStores] = useState<StoreLocation[] | null>(null);
  const [selectedStoreId, setSelectedStoreId] = useState<string>("");
  const [storeProducts, setStoreProducts] = useState<StoreProductTrends | null>(null);
  const [storeRecs, setStoreRecs] = useState<StoreLevelRecommendations | null>(null);

  useEffect(() => {
    let cancelled = false;
    setData(null);
    setSelectedState(null);
    api.trendRegions(category).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [category]);

  const handleCellClick = (region: string) => {
    setSelectedState(region);
    setStores(null);
    setSelectedStoreId("");
    setStoreProducts(null);
    setStoreRecs(null);
    api.regionStores(region).then((res) => setStores(res.stores));
  };

  const handleStoreSelect = (storeId: string) => {
    setSelectedStoreId(storeId);
    setStoreProducts(null);
    setStoreRecs(null);
    if (!storeId || !selectedState) return;
    api.storeProductTrends(selectedState, storeId, category).then(setStoreProducts);
    api.storeRecommendationsAt(selectedState, storeId, category, location).then(setStoreRecs);
  };

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
            className={r.region === selectedState ? "heatmap-cell heatmap-cell-selected" : "heatmap-cell"}
            style={{ backgroundColor: colorFor(r.value, max) }}
            title={`${r.region}: ${r.value}`}
            onClick={() => handleCellClick(r.region)}
          >
            <span className="heatmap-region">{r.region}</span>
            <span className="heatmap-value">{r.value}</span>
          </div>
        ))}
      </div>

      {selectedState && (
        <div className="store-drilldown">
          {stores === null ? (
            <p className="muted">Loading stores in {selectedState}...</p>
          ) : stores.length === 0 ? (
            <p className="muted" style={{ fontSize: 13 }}>
              No store location data available for {selectedState}.
            </p>
          ) : (
            <>
              <label className="store-select-label">
                Store in {selectedState}:
                <select
                  className="location-input"
                  value={selectedStoreId}
                  onChange={(e) => handleStoreSelect(e.target.value)}
                >
                  <option value="">Select a store...</option>
                  {stores.map((s) => (
                    <option key={s.store_id} value={s.store_id}>
                      {s.city} — {s.address}
                    </option>
                  ))}
                </select>
              </label>

              {selectedStoreId && (!storeProducts || !storeRecs) && (
                <p className="muted">Loading store data...</p>
              )}

              {storeProducts && storeRecs && (
                <div className="store-detail">
                  <p className="upload-warning" style={{ marginTop: 8 }}>
                    {storeProducts.note}
                  </p>
                  <h3 className="store-detail-heading">Trending at this store</h3>
                  <ul className="trending-list">
                    {[...storeProducts.products]
                      .sort((a, b) => b.change_pct - a.change_pct)
                      .slice(0, 5)
                      .map((p) => (
                        <li key={p.product} className="trending-row">
                          <span className="trending-label">{p.product}</span>
                          <span className={p.change_pct >= 0 ? "change-pct up" : "change-pct down"}>
                            {p.change_pct >= 0 ? "+" : ""}
                            {p.change_pct}%
                          </span>
                        </li>
                      ))}
                  </ul>
                  <h3 className="store-detail-heading">Top recommendations</h3>
                  <div className="store-rec-list">
                    {[...storeRecs.recommendations]
                      .sort((a, b) => {
                        const order = { high: 0, medium: 1, low: 2 };
                        return order[a.priority] - order[b.priority];
                      })
                      .slice(0, 4)
                      .map((r) => (
                        <div key={r.product} className={`store-rec-card priority-${r.priority}`}>
                          <div className="store-rec-top">
                            <span className="store-rec-product">{r.product}</span>
                            <span className={`priority-pill priority-${r.priority}`}>{r.priority}</span>
                          </div>
                          <div className="store-rec-action">{r.action}</div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
