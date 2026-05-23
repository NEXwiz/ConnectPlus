import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import { RoadmapSkeleton } from "../components/Skeleton";
import {
  Target,
  CheckCircle2,
  Circle,
  BookOpen,
  Hammer,
  Dumbbell,
  ChevronDown,
  ChevronRight,
  Archive,
  Loader2,
  Plus,
  ArrowLeft,
  ExternalLink,
  AlertTriangle,
  Sparkles,
} from "lucide-react";

interface Milestone {
  id: string;
  week: number;
  title: string;
  description: string;
  category: "learn" | "build" | "practice";
  resources: { title: string; url: string; type: string }[];
  is_completed: boolean;
}

interface Roadmap {
  id: string;
  title: string;
  target_role: string;
  gap_analysis: { missing_skills: string[]; weak_areas: string[]; strengths: string[] };
  timeline_weeks: number;
  status: string;
  milestones?: Milestone[];
  created_at: string;
}

const categoryIcon = { learn: BookOpen, build: Hammer, practice: Dumbbell };
const categoryColor = {
  learn: "text-blue-600 bg-blue-50",
  build: "text-amber-600 bg-amber-50",
  practice: "text-green-600 bg-green-50",
};

export default function RoadmapPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [roadmaps, setRoadmaps] = useState<Roadmap[]>([]);
  const [selected, setSelected] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [targetRole, setTargetRole] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) { navigate("/login"); return; }
    fetchRoadmaps();
  }, [user]);

  const fetchRoadmaps = async () => {
    setLoading(true);
    try {
      const { data } = await api.get("/api/roadmaps");
      setRoadmaps(data.roadmaps || []);
    } catch { /* ignore */ }
    setLoading(false);
  };

  const selectRoadmap = async (id: string) => {
    try {
      const { data } = await api.get(`/api/roadmaps/${id}`);
      setSelected(data);
    } catch { /* ignore */ }
  };

  const generateRoadmap = async () => {
    if (!targetRole.trim()) return;
    setGenerating(true);
    setError("");
    try {
      const { data } = await api.post("/api/roadmaps/generate", { target_role: targetRole.trim() });
      setSelected(data);
      setTargetRole("");
      fetchRoadmaps();
    } catch (e: any) {
      setError(e.response?.data?.detail || "Generation failed.");
    }
    setGenerating(false);
  };

  const toggleMilestone = async (milestoneId: string) => {
    if (!selected) return;
    try {
      const { data } = await api.put(`/api/roadmaps/${selected.id}/milestones/${milestoneId}/toggle`);
      setSelected({
        ...selected,
        milestones: selected.milestones?.map((m) => (m.id === milestoneId ? data : m)),
      });
    } catch { /* ignore */ }
  };

  const archiveRoadmap = async (id: string) => {
    try {
      await api.put(`/api/roadmaps/${id}/archive`);
      setSelected(null);
      fetchRoadmaps();
    } catch { /* ignore */ }
  };

  const progress = selected?.milestones
    ? Math.round((selected.milestones.filter((m) => m.is_completed).length / selected.milestones.length) * 100)
    : 0;

  if (loading) {
    return <RoadmapSkeleton />;
  }

  if (selected) {
    return (
      <div className="space-y-6">
        <button onClick={() => setSelected(null)} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to roadmaps
        </button>

        {/* Header */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold">{selected.title}</h1>
            <p className="text-muted-foreground">Target: {selected.target_role} · {selected.timeline_weeks} weeks</p>
          </div>
          <button onClick={() => archiveRoadmap(selected.id)} className="flex items-center gap-1 text-sm text-muted-foreground hover:text-destructive">
            <Archive className="h-4 w-4" /> Archive
          </button>
        </div>

        {/* Progress bar */}
        <div className="space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{progress}%</span>
          </div>
          <div className="h-2 rounded-full bg-muted">
            <div className="h-2 rounded-full bg-primary transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>

        {/* Gap Analysis */}
        <div className="grid gap-4 sm:grid-cols-3">
          <GapCard title="Strengths" items={selected.gap_analysis.strengths} color="text-green-700 bg-green-50" icon={CheckCircle2} />
          <GapCard title="Missing Skills" items={selected.gap_analysis.missing_skills} color="text-red-700 bg-red-50" icon={AlertTriangle} />
          <GapCard title="Weak Areas" items={selected.gap_analysis.weak_areas} color="text-amber-700 bg-amber-50" icon={Target} />
        </div>

        {/* Milestones */}
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Milestones</h2>
          {selected.milestones?.map((m) => (
            <MilestoneCard key={m.id} milestone={m} onToggle={() => toggleMilestone(m.id)} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Growth Roadmaps</h1>
      </div>

      {/* Generate form */}
      <div className="rounded-lg border border-border p-4 space-y-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          <Sparkles className="h-4 w-4 text-primary" />
          Generate a new roadmap
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Senior Frontend Engineer, ML Engineer..."
            className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
            onKeyDown={(e) => e.key === "Enter" && generateRoadmap()}
          />
          <button
            onClick={generateRoadmap}
            disabled={generating || !targetRole.trim()}
            className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {generating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
            {generating ? "Generating..." : "Generate"}
          </button>
        </div>
        {error && <p className="text-sm text-destructive">{error}</p>}
      </div>

      {/* Roadmap list */}
      {roadmaps.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-card/50 p-12 text-center">
          <Target className="mx-auto h-10 w-10 text-muted-foreground/50" />
          <h3 className="mt-3 text-sm font-semibold text-foreground">No roadmaps yet</h3>
          <p className="mt-1 text-sm text-muted-foreground max-w-sm mx-auto">
            Enter a target role above and generate a personalized learning path with milestones.
          </p>
        </div>
      ) : (
        <div className="grid gap-3">
          {roadmaps.filter((r) => r.status === "active").map((r) => (
            <button
              key={r.id}
              onClick={() => selectRoadmap(r.id)}
              className="flex items-center justify-between rounded-lg border border-border p-4 text-left hover:bg-accent hover:border-primary/30 transition-all duration-200"
            >
              <div>
                <p className="font-medium">{r.title}</p>
                <p className="text-sm text-muted-foreground">Target: {r.target_role} · {r.timeline_weeks} weeks</p>
              </div>
              <ChevronRight className="h-5 w-5 text-muted-foreground" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function GapCard({ title, items, color, icon: Icon }: { title: string; items: string[]; color: string; icon: any }) {
  return (
    <div className="rounded-lg border border-border p-4 space-y-2">
      <div className={`flex items-center gap-1.5 text-sm font-medium ${color.split(" ")[0]}`}>
        <Icon className="h-4 w-4" /> {title}
      </div>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-muted-foreground">• {item}</li>
        ))}
      </ul>
    </div>
  );
}

function MilestoneCard({ milestone, onToggle }: { milestone: Milestone; onToggle: () => void }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = categoryIcon[milestone.category] || BookOpen;
  const color = categoryColor[milestone.category] || categoryColor.learn;

  return (
    <div className="rounded-lg border border-border p-4 space-y-2">
      <div className="flex items-start gap-3">
        <button onClick={onToggle} className="mt-0.5 shrink-0">
          {milestone.is_completed ? (
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          ) : (
            <Circle className="h-5 w-5 text-muted-foreground hover:text-primary" />
          )}
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
              <Icon className="h-3 w-3" /> {milestone.category}
            </span>
            <span className="text-xs text-muted-foreground">Week {milestone.week}</span>
          </div>
          <p className={`font-medium mt-1 ${milestone.is_completed ? "line-through text-muted-foreground" : ""}`}>
            {milestone.title}
          </p>
        </div>
        <button onClick={() => setExpanded(!expanded)} className="shrink-0 text-muted-foreground hover:text-foreground">
          <ChevronDown className={`h-4 w-4 transition-transform ${expanded ? "rotate-180" : ""}`} />
        </button>
      </div>

      {expanded && (
        <div className="ml-8 space-y-2">
          {milestone.description && <p className="text-sm text-muted-foreground">{milestone.description}</p>}
          {milestone.resources?.length > 0 && (
            <div className="space-y-1">
              {milestone.resources.map((r, i) => (
                <a
                  key={i}
                  href={r.url || "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1.5 text-sm text-primary hover:underline"
                >
                  <ExternalLink className="h-3 w-3" /> {r.title}
                </a>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
