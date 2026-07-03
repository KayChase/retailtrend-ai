import type { TrendSeries } from "../types/api";

interface Props {
  trends: TrendSeries[];
  selected: string;
  onSelect: (key: string) => void;
}

export function TrendingList({ trends, selected, onSelect }: Props) {
  const sorted = [...trends].sort((a, b) => b.change_pct - a.change_pct);

  return (
    <div className="card">
      <div className="card-header">
        <h2>Trending Searches</h2>
        <span className="source-badge">{trends[0]?.source === "live" ? "Live" : "Sample data"}</span>
      </div>
      <ul className="trending-list">
        {sorted.map((t) => (
          <li
            key={t.category}
            className={t.category === selected ? "trending-row trending-row-active" : "trending-row"}
            onClick={() => onSelect(t.category)}
          >
            <span className="trending-label">{t.category.replace(/_/g, " ")}</span>
            <span className={t.change_pct >= 0 ? "change-pct up" : "change-pct down"}>
              {t.change_pct >= 0 ? "+" : ""}
              {t.change_pct}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
