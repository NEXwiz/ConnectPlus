import { useState, useEffect } from "react";
import { TrendingUp } from "lucide-react";
import api from "@/services/api";
import { HiringTrendsSkeleton } from "@/components/Skeleton";
import { cn } from "@/lib/utils";

interface Trends {
  total_jobs: number;
  tech_demand: Record<string, number>;
  role_demand: Record<string, number>;
  remote_percentage: number;
  experience_distribution: Record<string, number>;
  positioning: {
    skill_match_percentage: number;
    matching_jobs: number;
    strong_skills: Record<string, number>;
    missing_hot_skills: string[];
  } | null;
}

export default function HiringTrends() {
  const [trends, setTrends] = useState<Trends | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/resumes/trends")
      .then((res) => setTrends(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <HiringTrendsSkeleton />;
  }

  if (!trends || trends.total_jobs === 0) return null;

  const topTech = Object.entries(trends.tech_demand).slice(0, 8);
  const maxCount = topTech.length > 0 ? topTech[0][1] : 1;

  return (
    <div className="rounded-xl border border-border bg-card p-4 space-y-4">
      <div className="flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-primary" />
        <h3 className="text-sm font-semibold text-card-foreground">Hiring Trends</h3>
      </div>

      {/* Top tech */}
      <div>
        <p className="text-xs text-muted-foreground mb-2">Most demanded skills</p>
        <div className="space-y-1.5">
          {topTech.map(([tech, count]) => (
            <div key={tech} className="flex items-center gap-2">
              <span className="text-xs text-foreground w-20 truncate">{tech}</span>
              <div className="flex-1 h-1.5 rounded-full bg-secondary">
                <div
                  className="h-1.5 rounded-full bg-primary"
                  style={{ width: `${(count / maxCount) * 100}%` }}
                />
              </div>
              <span className="text-[10px] text-muted-foreground w-4 text-right">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Remote % */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Remote roles</span>
        <span className="font-semibold text-foreground">{trends.remote_percentage}%</span>
      </div>

      {/* Experience distribution */}
      <div>
        <p className="text-xs text-muted-foreground mb-1.5">Experience levels</p>
        <div className="flex gap-1">
          {Object.entries(trends.experience_distribution).map(([bucket, count]) => (
            <div key={bucket} className="flex-1 text-center">
              <div
                className={cn(
                  "mx-auto rounded-sm bg-primary/20",
                  "w-full"
                )}
                style={{ height: `${Math.max(8, (count / trends.total_jobs) * 60)}px` }}
              />
              <span className="text-[9px] text-muted-foreground mt-0.5 block">{bucket}y</span>
            </div>
          ))}
        </div>
      </div>

      {/* User positioning */}
      {trends.positioning && (
        <div className="pt-3 border-t border-border">
          <p className="text-xs font-medium text-foreground mb-1">
            Your skills match{" "}
            <span className="text-primary">{trends.positioning.skill_match_percentage}%</span>{" "}
            of roles ({trends.positioning.matching_jobs} jobs)
          </p>
          {trends.positioning.missing_hot_skills.length > 0 && (
            <p className="text-[10px] text-muted-foreground">
              Hot skills to learn:{" "}
              <span className="text-foreground">
                {trends.positioning.missing_hot_skills.join(", ")}
              </span>
            </p>
          )}
        </div>
      )}
    </div>
  );
}
