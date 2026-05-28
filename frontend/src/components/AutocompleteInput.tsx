import { useState, useRef, useEffect } from "react";

interface AutocompleteInputProps {
  options: string[];
  selected: string[];
  onAdd: (value: string) => void;
  placeholder?: string;
}

export default function AutocompleteInput({ options, selected, onAdd, placeholder }: AutocompleteInputProps) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const filtered = query.trim()
    ? options.filter(
        (o) => o.toLowerCase().includes(query.toLowerCase()) && !selected.includes(o)
      ).slice(0, 8)
    : [];

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleSelect = (value: string) => {
    onAdd(value);
    setQuery("");
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative">
      <input
        type="text"
        value={query}
        onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        placeholder={placeholder || "Search..."}
        className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/30 focus:border-primary/50 transition-all"
      />
      {open && filtered.length > 0 && (
        <ul className="absolute z-50 mt-1.5 w-full max-h-52 overflow-y-auto rounded-xl border border-border bg-card p-1 shadow-xl shadow-black/5 backdrop-blur-sm">
          {filtered.map((item) => (
            <li
              key={item}
              onClick={() => handleSelect(item)}
              className="px-3 py-2 text-sm text-foreground cursor-pointer rounded-lg hover:bg-primary/10 hover:text-primary transition-colors"
            >
              {item}
            </li>
          ))}
        </ul>
      )}
      {open && query.trim() && filtered.length === 0 && (
        <div className="absolute z-50 mt-1.5 w-full rounded-xl border border-border bg-card p-1 shadow-xl shadow-black/5">
          <p className="px-3 py-2 text-sm text-muted-foreground">No matches found</p>
        </div>
      )}
    </div>
  );
}
