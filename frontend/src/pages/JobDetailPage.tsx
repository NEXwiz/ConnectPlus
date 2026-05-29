import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  Building2,
  MapPin,
  Clock,
  Wifi,
  ExternalLink,
  Loader2,
  Banknote,
  Target,
  FileText,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import api from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";
import { useProfileCompletion } from "@/hooks/useProfileCompletion";
import ProfileGateBanner from "@/components/ProfileGateBanner";
import { JobDetailSkeleton } from "@/components/Skeleton";
import { cn } from "@/lib/utils";

const employmentLabels: Record<string, string> = {
  full_time: "Full Time",
  contract: "Contract",
  freelance: "Freelance",
  government: "Government",
  internship: "Internship",
};

interface Job {
  id: string;
  title: string;
  company: string;
  company_logo_url: string | null;
  description: string;
  requirements: string | null;
  employment_type: string;
  role_type: string;
  experience_min: number;
  experience_max: number | null;
  tech_stack: string[];
  location: string | null;
  is_remote: boolean;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  apply_url: string | null;
  created_at: string;
}

function formatSalary(min: number | null, max: number | null, currency: string) {
  if (!min && !max) return null;
  const fmt = (n: number) => {
    if (n >= 100000) return `${(n / 100000).toFixed(n % 100000 === 0 ? 0 : 1)}L`;
    if (n >= 1000) return `${(n / 1000).toFixed(0)}K`;
    return n.toString();
  };
  if (min && max) return `${fmt(min)} - ${fmt(max)} ${currency}`;
  if (min) return `${fmt(min)}+ ${currency}`;
  return `Up to ${fmt(max!)} ${currency}`;
}

export default function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const { user } = useAuth();
  const { isComplete: profileComplete, loading: profileLoading } = useProfileCompletion();
  const [job, setJob] = useState<Job | null>(null);
  const [fit, setFit] = useState<{ fit_score: number; breakdown: Record<string, number> } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const res = await api.get(`/api/jobs/${jobId}`);
        setJob(res.data);
      } catch (err: any) {
        setError(err.response?.status === 404 ? "Job not found." : "Failed to load job.");
      }
      setLoading(false);
    };
    fetchJob();
  }, [jobId]);

  useEffect(() => {
    if (!user || !jobId || !profileComplete) return;
    api.get(`/api/jobs/${jobId}/fit`).then((res) => {
      setFit(res.data);
    }).catch(() => {});
  }, [jobId, user, profileComplete]);

  if (loading) {
    return <JobDetailSkeleton />;
  }

  if (error || !job) {
    return (
      <div className="animate-fade-in text-center py-20">
        <p className="text-muted-foreground">{error || "Job not found."}</p>
        <Link to="/jobs" className="mt-4 inline-block text-sm text-primary hover:underline">
          Back to jobs
        </Link>
      </div>
    );
  }

  const expLabel =
    job.experience_max && job.experience_max > 0
      ? `${job.experience_min}-${job.experience_max} years`
      : job.experience_min > 0
        ? `${job.experience_min}+ years`
        : "Freshers welcome";

  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency);

  return (
    <div className="animate-fade-in max-w-3xl">
      {/* Back link */}
      <Link
        to="/jobs"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        All jobs
      </Link>

      {/* Header */}
      <div className="rounded-xl border border-border bg-card p-6">
        <h1 className="text-2xl font-bold text-card-foreground">{job.title}</h1>

        <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <Building2 className="h-4 w-4" />
            {job.company}
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="h-4 w-4" />
            {expLabel}
          </span>
          {job.location && (
            <span className="flex items-center gap-1.5">
              <MapPin className="h-4 w-4" />
              {job.location}
            </span>
          )}
          {job.is_remote && (
            <span className="flex items-center gap-1.5 text-primary">
              <Wifi className="h-4 w-4" />
              Remote
            </span>
          )}
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <span className="rounded-lg bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            {employmentLabels[job.employment_type] || job.employment_type}
          </span>
          {salary && (
            <span className="flex items-center gap-1 rounded-lg bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">
              <Banknote className="h-3 w-3" />
              {salary}
            </span>
          )}
        </div>

        {/* Tech stack */}
        {job.tech_stack.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1.5">
            {job.tech_stack.map((tech) => (
              <span
                key={tech}
                className="rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground"
              >
                {tech}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Fit Score */}
      {user && !profileComplete && !profileLoading && (
        <div className="mt-4">
          <ProfileGateBanner message="Complete your profile to see your fit score and tailor your resume" />
        </div>
      )}
      {fit && (
        <div className="mt-4 rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-3 mb-3">
            <Target className="h-5 w-5 text-primary" />
            <span className="text-lg font-bold text-card-foreground">
              {fit.fit_score}% Fit
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {Object.entries(fit.breakdown).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="h-2 rounded-full bg-secondary mb-1.5">
                  <div
                    className={cn(
                      "h-2 rounded-full",
                      value >= 70 ? "bg-green-500" : value >= 40 ? "bg-amber-500" : "bg-red-400"
                    )}
                    style={{ width: `${value}%` }}
                  />
                </div>
                <div className="text-xs text-muted-foreground">
                  {key.replace(/_/g, " ")}
                </div>
                <div className="text-sm font-semibold text-foreground">{value}%</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Description */}
      <div className="mt-6 rounded-xl border border-border bg-card p-6">
        <h2 className="text-lg font-semibold text-card-foreground">Description</h2>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground whitespace-pre-line">
          {job.description}
        </p>
      </div>

      {/* Requirements */}
      {job.requirements && (
        <div className="mt-4 rounded-xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Requirements</h2>
          <p className="mt-3 text-sm leading-relaxed text-muted-foreground whitespace-pre-line">
            {job.requirements}
          </p>
        </div>
      )}

      {/* Apply button */}
      {job.apply_url && (
        <div className="mt-6">
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Apply Now
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      )}

      {/* Resume Tailoring */}
      {user && profileComplete && <ResumeTailoring jobId={job.id} />}
      {user && profileComplete && <ResumeGenerator jobId={job.id} />}
    </div>
  );
}

function ResumeTailoring({ jobId }: { jobId: string }) {
  const [tailoring, setTailoring] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTailor = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post(`/api/resumes/tailor/${jobId}`);
      setTailoring(data.analysis);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Tailoring failed.");
    }
    setLoading(false);
  };

  if (tailoring) {
    const score = tailoring.match_score ?? 0;
    const isMismatch = score < 40;

    return (
      <div className="mt-6 space-y-4">
        {isMismatch && (
          <div className="rounded-xl border border-amber-300 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 p-4 flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-amber-800 dark:text-amber-300">Low match detected</p>
              <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
                Your resume scores {score}% for this role. Consider the suggestions below to improve alignment.
              </p>
            </div>
          </div>
        )}

        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              <span className="font-semibold text-card-foreground">Resume Match: {score}%</span>
            </div>
            <div className={cn(
              "h-2 w-24 rounded-full bg-secondary",
            )}>
              <div
                className={cn("h-2 rounded-full", score >= 70 ? "bg-green-500" : score >= 40 ? "bg-amber-500" : "bg-red-400")}
                style={{ width: `${score}%` }}
              />
            </div>
          </div>

          {tailoring.summary && (
            <p className="text-sm text-muted-foreground mb-4">{tailoring.summary}</p>
          )}

          <div className="grid gap-4 sm:grid-cols-2">
            {tailoring.strengths?.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-green-700 dark:text-green-400 uppercase mb-2">Strengths</h4>
                <ul className="space-y-1">
                  {tailoring.strengths.map((s: string, i: number) => (
                    <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                      <CheckCircle2 className="h-3 w-3 text-green-500 shrink-0 mt-0.5" />
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {tailoring.gaps?.length > 0 && (
              <div>
                <h4 className="text-xs font-semibold text-red-700 dark:text-red-400 uppercase mb-2">Gaps</h4>
                <ul className="space-y-1">
                  {tailoring.gaps.map((g: string, i: number) => (
                    <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                      <AlertCircle className="h-3 w-3 text-red-400 shrink-0 mt-0.5" />
                      {g}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {tailoring.suggestions?.length > 0 && (
            <div className="mt-4 pt-4 border-t border-border">
              <h4 className="text-xs font-semibold text-primary uppercase mb-2">Suggestions</h4>
              <ul className="space-y-1.5">
                {tailoring.suggestions.map((s: string, i: number) => (
                  <li key={i} className="text-xs text-muted-foreground">• {s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="mt-6 rounded-xl border border-border bg-card p-5 text-center">
      {error && (
        <p className="text-sm text-destructive mb-3">{error}</p>
      )}
      <button
        onClick={handleTailor}
        disabled={loading}
        className="inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary/90 disabled:opacity-50 transition-colors"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
        {loading ? "Analyzing..." : "Tailor Resume for This Role"}
      </button>
      <p className="text-xs text-muted-foreground mt-2">
        Analyzes your resume against this job's requirements
      </p>
    </div>
  );
}


function ResumeGenerator({ jobId }: { jobId: string }) {
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<{ tex_content: string; job_title: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const { data } = await api.post(`/api/resumes/generate/${jobId}`);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Generation failed.");
    }
    setGenerating(false);
  };

  const handleDownload = () => {
    if (!result) return;
    const blob = new Blob([result.tex_content], { type: "application/x-tex" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume_${result.job_title.replace(/\s+/g, "_").toLowerCase()}.tex`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleOverleaf = () => {
    if (!result) return;
    const blob = new Blob([result.tex_content], { type: "application/x-tex" });
    const url = URL.createObjectURL(blob);
    // Overleaf doesn't support data URIs directly; use their /docs endpoint with encoded content
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "https://www.overleaf.com/docs";
    form.target = "_blank";
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "snip";
    input.value = result.tex_content;
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
    URL.revokeObjectURL(url);
  };

  if (result) {
    return (
      <div className="mt-4 rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-950/20 p-5">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="h-5 w-5 text-green-600" />
          <span className="font-semibold text-foreground">Resume Generated</span>
        </div>
        <p className="text-sm text-muted-foreground mb-4">
          Tailored for: {result.job_title}
        </p>
        <div className="flex gap-3">
          <button
            onClick={handleDownload}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Download .tex
          </button>
          <button
            onClick={handleOverleaf}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            Open in Overleaf
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4 rounded-xl border border-border bg-card p-5 text-center">
      {error && <p className="text-sm text-destructive mb-3">{error}</p>}
      <button
        onClick={handleGenerate}
        disabled={generating}
        className="inline-flex items-center gap-2 rounded-lg border border-primary text-primary px-5 py-2.5 text-sm font-semibold hover:bg-primary/10 disabled:opacity-50 transition-colors"
      >
        {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
        {generating ? "Generating..." : "Generate Tailored Resume"}
      </button>
      <p className="text-xs text-muted-foreground mt-2">
        Creates a LaTeX resume optimized for this role
      </p>
    </div>
  );
}
