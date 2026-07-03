import type { CategoryInfo } from "../types/api";

interface Props {
  categories: CategoryInfo[];
  selected: string;
  onSelect: (key: string) => void;
}

export function CategorySelector({ categories, selected, onSelect }: Props) {
  return (
    <div className="category-selector">
      {categories.map((c) => (
        <button
          key={c.key}
          className={c.key === selected ? "chip chip-active" : "chip"}
          onClick={() => onSelect(c.key)}
        >
          {c.label}
        </button>
      ))}
    </div>
  );
}
