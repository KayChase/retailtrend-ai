import { useRef, useState } from "react";
import { api } from "../api/client";
import type { ReportAnalysisResult } from "../types/api";

export function ReportImageUpload() {
  const [result, setResult] = useState<ReportAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const csvInputRef = useRef<HTMLInputElement>(null);

  const runAnalysis = async (analyze: () => Promise<ReportAnalysisResult>) => {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyze();
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      if (imageInputRef.current) imageInputRef.current.value = "";
      if (csvInputRef.current) csvInputRef.current.value = "";
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreviewUrl(URL.createObjectURL(file));
    runAnalysis(() => api.analyzeReportImage(file));
  };

  const handleCsvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreviewUrl(null);
    runAnalysis(() => api.analyzeReportCsv(file));
  };

  const sorted = result
    ? [...result.recommendations].sort((a, b) => {
        const order = { high: 0, medium: 1, low: 2 };
        return order[a.priority] - order[b.priority];
      })
    : [];

  return (
    <div className="card">
      <div className="card-header">
        <h2>Analyze a Sales Report</h2>
        {result && <span className="source-badge">{result.source === "claude" ? "Claude" : "Rule-based"}</span>}
      </div>
      <p className="muted" style={{ fontSize: 13 }}>
        Upload a printed sales report — either a photo (Claude reads the table) or a CSV
        export (instant, no API key needed) — with columns like SKU, SKU Description, Total
        Sales, % vs Last Year, and Regular Sales. You'll get a recommendation for every item.
      </p>
      <div className="data-upload-controls">
        <label className="upload-button">
          {busy ? "Analyzing..." : "Upload report photo"}
          <input
            ref={imageInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            onChange={handleImageChange}
            disabled={busy}
            hidden
          />
        </label>
        <label className="upload-button">
          {busy ? "Analyzing..." : "Upload report CSV"}
          <input
            ref={csvInputRef}
            type="file"
            accept=".csv"
            onChange={handleCsvChange}
            disabled={busy}
            hidden
          />
        </label>
      </div>

      {previewUrl && (
        <img
          src={previewUrl}
          alt="Uploaded report preview"
          style={{ maxWidth: 200, marginTop: 12, borderRadius: 8, display: "block" }}
        />
      )}

      {error && <p className="upload-warning error">{error}</p>}

      {result && (
        <>
          <p className="muted" style={{ fontSize: 12, marginTop: 12 }}>
            Read {result.item_count} item{result.item_count === 1 ? "" : "s"} from the report.
          </p>
          <div className="store-rec-list" style={{ marginTop: 12 }}>
            {sorted.map((r) => (
              <div key={r.description} className={`store-rec-card priority-${r.priority}`}>
                <div className="store-rec-top">
                  <span className="store-rec-product">{r.description}</span>
                  <span className={`priority-pill priority-${r.priority}`}>{r.priority}</span>
                </div>
                <div className="store-rec-action">{r.action}</div>
                <div className="store-rec-tags">
                  <span>Demand: {r.expected_demand}</span>
                  {r.change_vs_ly_pct !== null && (
                    <span>
                      vs LY: {r.change_vs_ly_pct >= 0 ? "+" : ""}
                      {r.change_vs_ly_pct}%
                    </span>
                  )}
                  {r.total_sales !== null && <span>Total sales: ${r.total_sales}</span>}
                  <span>{r.order_more ? "Order more" : "No reorder"}</span>
                  <span>{r.increase_facings ? "Expand shelf space" : "Keep shelf space"}</span>
                </div>
                <p className="store-rec-text">{r.placement_suggestion}</p>
                <p className="store-rec-text muted">{r.reasoning}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
