import { useState, useEffect } from "react";
import api from "@/services/api";

interface MarqueeJob {
  id: string;
  title: string;
  company: string;
  tech_stack: string[];
  is_remote: boolean;
}

function MarqueeRow({ jobs, direction }: { jobs: MarqueeJob[]; direction: "left" | "right" }) {
  const doubled = [...jobs, ...jobs];
  return (
    <div className="overflow-hidden">
      <div
        className={`flex gap-4 w-max ${direction === "left" ? "animate-marquee-left" : "animate-marquee-right"}`}
      >
        {doubled.map((job, i) => (
          <div
            key={`${job.id}-${i}`}
            className="flex-shrink-0 rounded-lg border border-border bg-card px-4 py-3 w-64"
          >
            <p className="text-sm font-medium text-foreground truncate">{job.title}</p>
            <div className="blur-[2px] mt-1.5 space-y-1">
              <p className="text-xs text-muted-foreground truncate">{job.company}</p>
              <div className="flex gap-1">
                {job.tech_stack.slice(0, 3).map((t) => (
                  <span key={t} className="rounded bg-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-foreground">
                    {t}
                  </span>
                ))}
              </div>
              {job.is_remote && <p className="text-[10px] text-primary">Remote</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function JobMarquee() {
  const [jobs, setJobs] = useState<MarqueeJob[]>([]);

  useEffect(() => {
    api.get("/api/jobs", { params: { page: 1, limit: 20 } })
      .then((r) => setJobs(r.data.jobs || []))
      .catch(() => {});
  }, []);

  if (jobs.length < 6) return null;

  const mid = Math.ceil(jobs.length / 2);
  const row1 = jobs.slice(0, mid);
  const row2 = jobs.slice(mid);

  return (
    <section className="py-8 space-y-4 overflow-hidden">
      <MarqueeRow jobs={row1} direction="left" />
      <MarqueeRow jobs={row2} direction="right" />
    </section>
  );
}
