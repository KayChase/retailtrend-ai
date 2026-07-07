import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { DataStatus } from "../types/api";

interface Props {
  onDataChanged: () => void;
}

export function DataUpload({ onDataChanged }: Props) {
  const [status, setStatus] = useState<DataStatus | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const refreshStatus = () => {
    api.dataStatus().then(setStatus).catch(() => undefined);
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setError(null);
    setWarnings([]);
    try {
      const result = await api.uploadData(file);
      setWarnings(result.warnings);
      refreshStatus();
      onDataChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleReset = async () => {
    setBusy(true);
    setError(null);
    setWarnings([]);
    try {
      await api.resetData();
      refreshStatus();
      onDataChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card data-upload-card">
      <div className="card-header">
        <h2>Data Source</h2>
        <span className="source-badge">
          {status?.using_uploaded_data ? "Your uploaded data" : "Sample data"}
        </span>
      </div>
      <p className="muted" style={{ fontSize: 13 }}>
        By default this dashboard runs on synthetic sample sales. Upload a CSV with{" "}
        <code>date, category, units_sold</code> (optionally <code>region</code>) columns to see
        the forecasts and recommendations run on your own numbers instead.
      </p>
      <div className="data-upload-controls">
        <label className="upload-button">
          {busy ? "Uploading..." : "Upload sales CSV"}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            disabled={busy}
            hidden
          />
        </label>
        {status?.using_uploaded_data && (
          <button className="chip" onClick={handleReset} disabled={busy}>
            Reset to sample data
          </button>
        )}
      </div>
      {status && (
        <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
          {status.rows.toLocaleString()} rows &middot; {status.date_range.start} to{" "}
          {status.date_range.end} &middot; {status.categories.length} categories
          {!status.has_region_data && " · no region breakdown"}
        </p>
      )}
      {warnings.map((w) => (
        <p key={w} className="upload-warning">
          {w}
        </p>
      ))}
      {error && <p className="upload-warning error">{error}</p>}
    </div>
  );
}
