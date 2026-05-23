import { cn } from "@/lib/utils";
import { Filter, X } from "lucide-react";

interface JobFiltersProps {
  filters: {
    employment_type: string;
    role_type: string;
    is_remote: string;
    experience_level: string;
    tech_stack: string;
  };
  onChange: (key: string, value: string) => void;
  onClear: () => void;
}

const employmentOptions = [
  { value: "", label: "All Types" },
  { value: "full_time", label: "Full Time" },
  { value: "contract", label: "Contract" },
  { value: "freelance", label: "Freelance" },
  { value: "government", label: "Government" },
  { value: "internship", label: "Internship" },
];

const roleOptions = [
  { value: "", label: "All Roles" },
  { value: "backend", label: "Backend" },
  { value: "frontend", label: "Frontend" },
  { value: "fullstack", label: "Full Stack" },
  { value: "ml", label: "ML / AI" },
  { value: "devops", label: "DevOps / SRE" },
  { value: "mobile", label: "Mobile" },
  { value: "data", label: "Data" },
  { value: "security", label: "Security" },
  { value: "qa", label: "QA" },
];

const experienceOptions = [
  { value: "", label: "Any Experience" },
  { value: "0", label: "Freshers (0 yrs)" },
  { value: "2", label: "2+ years" },
  { value: "3", label: "3+ years" },
  { value: "5", label: "5+ years" },
  { value: "8", label: "8+ years" },
];

export default function JobFilters({ filters, onChange, onClear }: JobFiltersProps) {
  const hasActiveFilters = Object.values(filters).some((v) => v !== "");

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-card-foreground">
          <Filter className="h-4 w-4" />
          Filters
        </div>
        {hasActiveFilters && (
          <button
            onClick={onClear}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-3 w-3" />
            Clear
          </button>
        )}
      </div>

      <div className="space-y-3">
        <FilterSelect
          label="Employment"
          value={filters.employment_type}
          options={employmentOptions}
          onChange={(v) => onChange("employment_type", v)}
        />
        <FilterSelect
          label="Role"
          value={filters.role_type}
          options={roleOptions}
          onChange={(v) => onChange("role_type", v)}
        />
        <FilterSelect
          label="Experience"
          value={filters.experience_level}
          options={experienceOptions}
          onChange={(v) => onChange("experience_level", v)}
        />

        {/* Remote toggle */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Remote
          </label>
          <div className="flex gap-1.5">
            {[
              { value: "", label: "Any" },
              { value: "true", label: "Remote" },
              { value: "false", label: "On-site" },
            ].map((opt) => (
              <button
                key={opt.value}
                onClick={() => onChange("is_remote", opt.value)}
                className={cn(
                  "rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                  filters.is_remote === opt.value
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground hover:bg-accent"
                )}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tech stack text input */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Tech Stack
          </label>
          <input
            type="text"
            value={filters.tech_stack}
            onChange={(e) => onChange("tech_stack", e.target.value)}
            placeholder="React, Python..."
            className="w-full rounded-lg border border-input bg-background px-3 py-1.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
      </div>
    </div>
  );
}

// Reusable select dropdown
function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: { value: string; label: string }[];
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-muted-foreground mb-1">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-input bg-background px-3 py-1.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}
