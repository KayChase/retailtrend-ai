import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { WeatherOutlook as WeatherOutlookData } from "../types/api";

interface Props {
  location: string;
  onLocationChange: (location: string) => void;
}

export function WeatherOutlook({ location, onLocationChange }: Props) {
  const [data, setData] = useState<WeatherOutlookData | null>(null);
  const [inputValue, setInputValue] = useState(location);

  useEffect(() => {
    let cancelled = false;
    api.weather(location).then((res) => {
      if (!cancelled) setData(res);
    });
    return () => {
      cancelled = true;
    };
  }, [location]);

  const submitLocation = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) onLocationChange(inputValue.trim());
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2>Weather Outlook{data ? ` — ${data.location}` : ""}</h2>
        <span className="source-badge">{data?.source === "live" ? "Live" : "Sample data"}</span>
      </div>
      <form className="location-form" onSubmit={submitLocation}>
        <input
          className="location-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="City, state, or zip"
        />
        <button type="submit" className="chip">
          Update
        </button>
      </form>
      {!data ? (
        <p className="muted">Loading...</p>
      ) : (
        <div className="weather-days">
          {data.days.map((d) => (
            <div key={d.date} className="weather-day">
              <span className="weather-date">
                {new Date(d.date + "T00:00:00").toLocaleDateString(undefined, {
                  weekday: "short",
                  month: "numeric",
                  day: "numeric",
                })}
              </span>
              <span className="weather-temp">
                {Math.round(d.temp_max)}° / {Math.round(d.temp_min)}°
              </span>
              <span className="weather-precip">{Math.round(d.precipitation_probability)}% rain</span>
            </div>
          ))}
        </div>
      )}
      <p className="muted" style={{ fontSize: 12, marginTop: 8 }}>
        Weather-sensitive products (sunscreen, cold/flu remedies, summer drinks, etc.) in Store
        Recommendations factor this outlook into their demand estimate.
      </p>
    </div>
  );
}
