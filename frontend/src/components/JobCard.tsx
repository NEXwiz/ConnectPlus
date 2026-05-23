import { cn } from "@/lib/utils";
import {
  MapPin,
  Building2,
  Clock,
  Wifi,
} from "lucide-react";
import { Link } from "react-router-dom";

interface JobCardProps {
  id: string;
  title: string;
  company: string;
  employment_type: string;
  role_type: string;
  tech_stack: string[];
  experience_min: number;
  experience_max: number | null;
  location: string | null;
  is_remote: boolean;
  similarity?: number;
  fitScore?: number;
}

const employmentLabels: Record<string, string> = {
  full_time: "Full Time",
  contract: "Contract",
  freelance: "Freelance",
  government: "Government",
  internship: "Internship",
};

export default function JobCard({
  id,
  title,
  company,
  employment_type,
  role_type,
  tech_stack,
  experience_min,
  experience_max,
  location,
  is_remote,
  similarity,
  fitScore,
}: JobCardProps) {
  const expLabel =
    experience_max && experience_max > 0
      ? `${experience_min}-${experience_max} yrs`
      : experience_min > 0
        ? `${experience_min}+ yrs`
        : "Freshers";

  return (
    <Link
      to={`/jobs/${id}`}
      className="group block rounded-xl border border-border bg-card p-5 transition-all duration-200 hover:border-primary/40 hover:shadow-md hover:-translate-y-0.5"
    >
      <div className="flex items-start justify-between gap-4">
        {/* Left: title and company */}
        <div className="min-w-0 flex-1">
          <h3 className="text-base font-semibold text-card-foreground group-hover:text-primary transition-colors truncate">
            {title}
          </h3>
          <div className="mt-1 flex items-center gap-2 text-sm text-muted-foreground">
            <Building2 className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{company}</span>
          </div>
        </div>

        {/* Right: match score badge (only for search results) */}
        {similarity !== undefined && (
          <span
            className={cn(
              "shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium",
              similarity >= 0.7
                ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                : similarity >= 0.5
                  ? "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                  : "bg-muted text-muted-foreground"
            )}
          >
            {Math.round(similarity * 100)}% match
          </span>
        )}
        {fitScore !== undefined && !similarity && (
          <span
            className={cn(
              "shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium",
              fitScore >= 70
                ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
                : fitScore >= 40
                  ? "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400"
                  : "bg-muted text-muted-foreground"
            )}
          >
            {fitScore}% fit
          </span>
        )}
      </div>

      {/* Meta row */}
      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {expLabel}
        </span>
        <span className="rounded bg-secondary px-2 py-0.5 font-medium text-secondary-foreground">
          {employmentLabels[employment_type] || employment_type}
        </span>
        {location && (
          <span className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {location}
          </span>
        )}
        {is_remote && (
          <span className="flex items-center gap-1 text-primary">
            <Wifi className="h-3 w-3" />
            Remote
          </span>
        )}
      </div>

      {/* Tech stack tags */}
      {tech_stack.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {tech_stack.slice(0, 6).map((tech) => (
            <span
              key={tech}
              className="rounded-md bg-accent px-2 py-0.5 text-xs font-medium text-accent-foreground"
            >
              {tech}
            </span>
          ))}
          {tech_stack.length > 6 && (
            <span className="text-xs text-muted-foreground">
              +{tech_stack.length - 6} more
            </span>
          )}
        </div>
      )}
    </Link>
  );
}
