import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import api from "@/services/api";
import {
  User,
  Save,
  Loader2,
  Plus,
  X,
  CheckCircle2,
  AlertCircle,
  GitFork,
  RefreshCw,
  Sparkles,
  Star,
  Unlink,
  FileUp,
  Trash2,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Profile {
  full_name: string;
  headline: string;
  bio: string;
  target_roles: string[];
  primary_skills: string[];
  secondary_skills: string[];
  experience_years: number;
  skill_experience: Record<string, number>;
  preferred_employment_types: string[];
  preferred_locations: string[];
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  open_to_remote: boolean;
  strengths: string[];
  areas_to_improve: string[];
  github_username: string;
  leetcode_username: string;
  codeforces_username: string;
}

interface Completion {
  is_complete: boolean;
  progress: number;
  missing_fields: string[];
}

const emptyProfile: Profile = {
  full_name: "",
  headline: "",
  bio: "",
  target_roles: [],
  primary_skills: [],
  secondary_skills: [],
  experience_years: 0,
  skill_experience: {},
  preferred_employment_types: [],
  preferred_locations: [],
  salary_min: null,
  salary_max: null,
  salary_currency: "INR",
  open_to_remote: true,
  strengths: [],
  areas_to_improve: [],
  github_username: "",
  leetcode_username: "",
  codeforces_username: "",
};

const employmentOptions = [
  "full_time",
  "contract",
  "freelance",
  "government",
  "internship",
];

const employmentLabels: Record<string, string> = {
  full_time: "Full Time",
  contract: "Contract",
  freelance: "Freelance",
  government: "Government",
  internship: "Internship",
};

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<Profile>(emptyProfile);
  const [completion, setCompletion] = useState<Completion | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Tag input states
  const [roleInput, setRoleInput] = useState("");
  const [primarySkillInput, setPrimarySkillInput] = useState("");
  const [secondarySkillInput, setSecondarySkillInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [strengthInput, setStrengthInput] = useState("");
  const [improveInput, setImproveInput] = useState("");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const [profileRes, completionRes] = await Promise.all([
        api.get("/api/profiles"),
        api.get("/api/profiles/completion"),
      ]);
      setProfile({ ...emptyProfile, ...profileRes.data });
      setCompletion(completionRes.data);
    } catch (err) {
      console.error("Failed to load profile:", err);
    }
    setLoading(false);
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSaved(false);
    try {
      await api.put("/api/profiles", profile);
      const completionRes = await api.get("/api/profiles/completion");
      setCompletion(completionRes.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to save profile");
    }
    setSaving(false);
  };

  const addTag = (
    field: keyof Profile,
    value: string,
    setter: (v: string) => void
  ) => {
    const trimmed = value.trim();
    if (!trimmed) return;
    const arr = profile[field] as string[];
    if (!arr.includes(trimmed)) {
      setProfile({ ...profile, [field]: [...arr, trimmed] });
    }
    setter("");
  };

  const removeTag = (field: keyof Profile, value: string) => {
    const arr = profile[field] as string[];
    setProfile({ ...profile, [field]: arr.filter((v) => v !== value) });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20 animate-fade-in">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in max-w-2xl">
      {/* Header */}
      <div className="sticky top-16 z-10 -mx-4 px-4 py-3 bg-background/95 backdrop-blur flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <User className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-2xl font-bold text-foreground">Profile</h1>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : saved ? (
            <CheckCircle2 className="h-4 w-4" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          {saving ? "Saving..." : saved ? "Saved!" : "Save"}
        </button>
      </div>

      {/* Completion indicator */}
      {completion && (
        <div className="mb-6 rounded-xl border border-border bg-card p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-card-foreground">
              Profile Completion
            </span>
            <span
              className={cn(
                "text-sm font-semibold",
                completion.progress >= 80
                  ? "text-green-600 dark:text-green-400"
                  : completion.progress >= 50
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-muted-foreground"
              )}
            >
              {completion.progress}%
            </span>
          </div>
          {/* -> progress bar */}
          <div className="h-2 rounded-full bg-secondary">
            <div
              className={cn(
                "h-2 rounded-full transition-all duration-500",
                completion.progress >= 80
                  ? "bg-green-500"
                  : completion.progress >= 50
                    ? "bg-amber-500"
                    : "bg-primary"
              )}
              style={{ width: `${completion.progress}%` }}
            />
          </div>
          {completion.missing_fields.length > 0 && (
            <p className="mt-2 text-xs text-muted-foreground">
              Missing:{" "}
              {completion.missing_fields
                .map((f) => f.replace(/_/g, " "))
                .join(", ")}
            </p>
          )}
        </div>
      )}

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* ─── Basic Info ─── */}
        <Section title="Basic Info">
          <Field label="Full Name">
            <input
              type="text"
              value={profile.full_name}
              onChange={(e) =>
                setProfile({ ...profile, full_name: e.target.value })
              }
              placeholder="Your full name"
              className="input-field"
            />
          </Field>
          <Field label="Headline">
            <input
              type="text"
              value={profile.headline}
              onChange={(e) =>
                setProfile({ ...profile, headline: e.target.value })
              }
              placeholder="e.g. Full Stack Developer | 3 years experience"
              className="input-field"
            />
          </Field>
          <Field label="Bio">
            <textarea
              value={profile.bio || ""}
              onChange={(e) =>
                setProfile({ ...profile, bio: e.target.value })
              }
              placeholder="A short paragraph about yourself, what you're working on, and what you're looking for..."
              rows={3}
              className="input-field resize-none"
            />
          </Field>
          <Field label="Total Experience (years)">
            <input
              type="number"
              min={0}
              max={50}
              value={profile.experience_years || ""}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  experience_years: parseInt(e.target.value) || 0,
                })
              }
              placeholder="0"
              className="input-field w-24"
            />
          </Field>
        </Section>

        {/* ─── Skills ─── */}
        <Section title="Skills">
          <Field label="Primary Skills" hint="Your strongest technical skills">
            <TagInput
              tags={profile.primary_skills}
              input={primarySkillInput}
              setInput={setPrimarySkillInput}
              onAdd={() =>
                addTag("primary_skills", primarySkillInput, setPrimarySkillInput)
              }
              onRemove={(v) => removeTag("primary_skills", v)}
              placeholder="e.g. Python, React, PostgreSQL"
            />
          </Field>
          <Field
            label="Secondary Skills"
            hint="Skills you're familiar with but not expert in"
          >
            <TagInput
              tags={profile.secondary_skills}
              input={secondarySkillInput}
              setInput={setSecondarySkillInput}
              onAdd={() =>
                addTag(
                  "secondary_skills",
                  secondarySkillInput,
                  setSecondarySkillInput
                )
              }
              onRemove={(v) => removeTag("secondary_skills", v)}
              placeholder="e.g. Docker, AWS, GraphQL"
            />
          </Field>
          {/* Skill Experience (years per skill) */}
          {(profile.primary_skills.length > 0 || profile.secondary_skills.length > 0) && (
            <Field label="Years per Skill" hint="How many years for each skill">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {[...profile.primary_skills, ...profile.secondary_skills].map((skill) => (
                  <div key={skill} className="flex items-center gap-2">
                    <span className="text-xs text-foreground w-24 truncate">{skill}</span>
                    <input
                      type="number"
                      min={0}
                      max={30}
                      value={profile.skill_experience[skill] || ""}
                      onChange={(e) =>
                        setProfile({
                          ...profile,
                          skill_experience: {
                            ...profile.skill_experience,
                            [skill]: parseInt(e.target.value) || 0,
                          },
                        })
                      }
                      placeholder="0"
                      className="input-field w-16 text-center"
                    />
                    <span className="text-[10px] text-muted-foreground">yrs</span>
                  </div>
                ))}
              </div>
            </Field>
          )}
        </Section>

        {/* ─── Target Roles & Preferences ─── */}
        <Section title="Target Roles & Preferences">
          <Field label="Target Roles" hint="Ordered by preference">
            <TagInput
              tags={profile.target_roles}
              input={roleInput}
              setInput={setRoleInput}
              onAdd={() => addTag("target_roles", roleInput, setRoleInput)}
              onRemove={(v) => removeTag("target_roles", v)}
              placeholder="e.g. Backend Engineer, Full Stack Developer"
            />
          </Field>
          <Field label="Preferred Employment Types">
            <div className="flex flex-wrap gap-2">
              {employmentOptions.map((opt) => (
                <button
                  key={opt}
                  type="button"
                  onClick={() => {
                    const types = profile.preferred_employment_types;
                    setProfile({
                      ...profile,
                      preferred_employment_types: types.includes(opt)
                        ? types.filter((t) => t !== opt)
                        : [...types, opt],
                    });
                  }}
                  className={cn(
                    "rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                    profile.preferred_employment_types.includes(opt)
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground hover:bg-accent"
                  )}
                >
                  {employmentLabels[opt]}
                </button>
              ))}
            </div>
          </Field>
          <Field label="Preferred Locations">
            <TagInput
              tags={profile.preferred_locations}
              input={locationInput}
              setInput={setLocationInput}
              onAdd={() =>
                addTag(
                  "preferred_locations",
                  locationInput,
                  setLocationInput
                )
              }
              onRemove={(v) => removeTag("preferred_locations", v)}
              placeholder="e.g. Bangalore, Remote, Mumbai"
            />
          </Field>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={profile.open_to_remote}
                onChange={(e) =>
                  setProfile({ ...profile, open_to_remote: e.target.checked })
                }
                className="rounded border-input"
              />
              <span className="text-sm text-foreground">Open to remote</span>
            </label>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Field label="Min Salary (annual)">
              <input
                type="number"
                value={profile.salary_min || ""}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    salary_min: parseInt(e.target.value) || null,
                  })
                }
                placeholder="e.g. 1500000"
                className="input-field"
              />
            </Field>
            <Field label="Max Salary (annual)">
              <input
                type="number"
                value={profile.salary_max || ""}
                onChange={(e) =>
                  setProfile({
                    ...profile,
                    salary_max: parseInt(e.target.value) || null,
                  })
                }
                placeholder="e.g. 3000000"
                className="input-field"
              />
            </Field>
          </div>
        </Section>

        {/* ─── Self Assessment ─── */}
        <Section title="Self Assessment">
          <Field label="Strengths" hint="What you're best at">
            <TagInput
              tags={profile.strengths}
              input={strengthInput}
              setInput={setStrengthInput}
              onAdd={() =>
                addTag("strengths", strengthInput, setStrengthInput)
              }
              onRemove={(v) => removeTag("strengths", v)}
              placeholder="e.g. System design, Fast learner, Clean code"
            />
          </Field>
          <Field label="Areas to Improve" hint="What you're working on">
            <TagInput
              tags={profile.areas_to_improve}
              input={improveInput}
              setInput={setImproveInput}
              onAdd={() =>
                addTag("areas_to_improve", improveInput, setImproveInput)
              }
              onRemove={(v) => removeTag("areas_to_improve", v)}
              placeholder="e.g. DevOps, Testing, Communication"
            />
          </Field>
        </Section>

        {/* ─── Platform Connections ─── */}
        <Section title="Platform Connections">
          <GitHubConnection />
          <Field label="LeetCode Username">
            <input
              type="text"
              value={profile.leetcode_username}
              onChange={(e) =>
                setProfile({ ...profile, leetcode_username: e.target.value })
              }
              placeholder="your-leetcode-username"
              className="input-field"
            />
          </Field>
          <Field label="Codeforces Username">
            <input
              type="text"
              value={profile.codeforces_username}
              onChange={(e) =>
                setProfile({
                  ...profile,
                  codeforces_username: e.target.value,
                })
              }
              placeholder="your-codeforces-handle"
              className="input-field"
            />
          </Field>
          <CPStats />
        </Section>

        {/* ─── Resume ─── */}
        <Section title="Resume">
          <ResumeSection />
        </Section>
      </div>
    </div>
  );
}

// ─── Sub-components ─────────────────────────────────────────

interface GitHubRepo {
  id: string;
  repo_name: string;
  repo_url: string;
  description: string | null;
  languages: Record<string, number>;
  topics: string[];
  stars: number;
  inferred_tech_stack: string[];
  ai_summary: string | null;
  relevance_scores: Record<string, number>;
}

function GitHubConnection() {
  const [connected, setConnected] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      const { data } = await api.get("/api/github/status");
      setConnected(data.connected);
      setUsername(data.username);
      if (data.connected) {
        const reposRes = await api.get("/api/github/repos");
        setRepos(reposRes.data.repos);
      }
    } catch (err) {
      console.error("GitHub status check failed:", err);
    }
    setLoading(false);
  };

  const connectGitHub = async () => {
    try {
      const { data } = await api.get("/api/github/auth");
      window.location.href = data.url;
    } catch (err) {
      console.error("Failed to initiate GitHub OAuth:", err);
    }
  };

  const disconnect = async () => {
    await api.delete("/api/github/disconnect");
    setConnected(false);
    setUsername(null);
    setRepos([]);
  };

  const syncRepos = async () => {
    setSyncing(true);
    try {
      const { data } = await api.post("/api/github/repos/sync");
      setRepos(data.repos);
    } catch (err) {
      console.error("Sync failed:", err);
    }
    setSyncing(false);
  };

  const analyzeAll = async () => {
    setAnalyzing(true);
    try {
      const { data } = await api.post("/api/github/repos/analyze");
      setRepos(data.repos);
    } catch (err) {
      console.error("Analysis failed:", err);
    }
    setAnalyzing(false);
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" /> Checking GitHub...
      </div>
    );
  }

  if (!connected) {
    return (
      <div>
        <label className="block text-sm font-medium text-foreground mb-1">
          GitHub
        </label>
        <button
          onClick={connectGitHub}
          className="flex items-center gap-2 rounded-lg bg-[#24292f] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#24292f]/90 transition-colors"
        >
          <GitFork className="h-4 w-4" />
          Connect GitHub
        </button>
        <p className="text-xs text-muted-foreground mt-1">
          Connect to analyze your repos and get role-fit insights
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <GitFork className="h-4 w-4" />
          <span className="text-sm font-medium text-foreground">
            Connected as{" "}
            <a
              href={`https://github.com/${username}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              @{username}
            </a>
          </span>
        </div>
        <button
          onClick={disconnect}
          className="flex items-center gap-1 text-xs text-muted-foreground hover:text-destructive transition-colors"
        >
          <Unlink className="h-3 w-3" /> Disconnect
        </button>
      </div>

      <div className="flex gap-2 mb-3">
        <button
          onClick={syncRepos}
          disabled={syncing}
          className="flex items-center gap-1.5 rounded-lg bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-accent transition-colors disabled:opacity-50"
        >
          <RefreshCw className={cn("h-3 w-3", syncing && "animate-spin")} />
          {syncing ? "Syncing..." : "Sync Repos"}
        </button>
        {repos.length > 0 && (
          <button
            onClick={analyzeAll}
            disabled={analyzing}
            className="flex items-center gap-1.5 rounded-lg bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
          >
            <Sparkles className={cn("h-3 w-3", analyzing && "animate-pulse")} />
            {analyzing ? "Analyzing..." : "Analyze All"}
          </button>
        )}
      </div>

      {repos.length > 0 && (
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {repos.map((repo) => (
            <div
              key={repo.id}
              className="rounded-lg border border-border p-3 text-sm"
            >
              <div className="flex items-center justify-between">
                <a
                  href={repo.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-foreground hover:text-primary"
                >
                  {repo.repo_name.split("/")[1]}
                </a>
                {repo.stars > 0 && (
                  <span className="flex items-center gap-0.5 text-xs text-muted-foreground">
                    <Star className="h-3 w-3" /> {repo.stars}
                  </span>
                )}
              </div>
              {repo.description && (
                <p className="text-xs text-muted-foreground mt-1">
                  {repo.description}
                </p>
              )}
              {repo.inferred_tech_stack.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {repo.inferred_tech_stack.map((tech) => (
                    <span
                      key={tech}
                      className="rounded bg-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-foreground"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              )}
              {repo.ai_summary && (
                <p className="text-xs text-muted-foreground mt-2 italic">
                  {repo.ai_summary}
                </p>
              )}
              {Object.keys(repo.relevance_scores).length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(repo.relevance_scores).map(([role, score]) => (
                    <span
                      key={role}
                      className="text-[10px] text-muted-foreground"
                    >
                      {role}:{" "}
                      <span className="font-semibold text-foreground">
                        {score}%
                      </span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {repos.length === 0 && (
        <p className="text-xs text-muted-foreground">
          No repos synced yet. Click "Sync Repos" to fetch your repositories.
        </p>
      )}
    </div>
  );
}

function CPStats() {
  const [profiles, setProfiles] = useState<any[]>([]);
  const [syncing, setSyncing] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const { data } = await api.get("/api/cp");
      setProfiles(data.profiles);
    } catch (err) {
      console.error("Failed to load CP stats:", err);
    }
    setLoaded(true);
  };

  const syncStats = async () => {
    setSyncing(true);
    try {
      const { data } = await api.post("/api/cp/sync");
      setProfiles(data.profiles);
    } catch (err) {
      console.error("CP sync failed:", err);
    }
    setSyncing(false);
  };

  if (!loaded) return null;

  return (
    <div className="pt-3 border-t border-border">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-foreground">CP Stats</span>
        <button
          onClick={syncStats}
          disabled={syncing}
          className="flex items-center gap-1.5 rounded-lg bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-accent transition-colors disabled:opacity-50"
        >
          <RefreshCw className={cn("h-3 w-3", syncing && "animate-spin")} />
          {syncing ? "Syncing..." : "Sync Stats"}
        </button>
      </div>

      {profiles.length === 0 && (
        <p className="text-xs text-muted-foreground">
          Add your usernames above and click "Sync Stats" to fetch your data.
        </p>
      )}

      <div className="grid gap-3">
        {profiles.map((p: any) => (
          <div
            key={p.id}
            className="rounded-lg border border-border p-3"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold uppercase text-muted-foreground">
                {p.platform}
              </span>
              <span className="text-xs text-muted-foreground">@{p.username}</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center">
              <div>
                <div className="text-lg font-bold text-foreground">
                  {p.problems_solved ?? "—"}
                </div>
                <div className="text-[10px] text-muted-foreground">Solved</div>
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">
                  {p.rating ?? "—"}
                </div>
                <div className="text-[10px] text-muted-foreground">Rating</div>
              </div>
              <div>
                <div className="text-lg font-bold text-foreground">
                  {p.rank ?? "—"}
                </div>
                <div className="text-[10px] text-muted-foreground">Rank</div>
              </div>
            </div>
            {p.platform === "leetcode" && p.stats?.by_difficulty && (
              <div className="flex gap-3 mt-2 text-[10px]">
                <span className="text-green-600">Easy: {p.stats.by_difficulty.easy ?? 0}</span>
                <span className="text-amber-600">Med: {p.stats.by_difficulty.medium ?? 0}</span>
                <span className="text-red-600">Hard: {p.stats.by_difficulty.hard ?? 0}</span>
              </div>
            )}
            {p.platform === "codeforces" && p.max_rating && (
              <div className="text-[10px] text-muted-foreground mt-2">
                Max Rating: {p.max_rating}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ResumeSection() {
  const [resumes, setResumes] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      const { data } = await api.get("/api/resumes");
      setResumes(data.resumes);
    } catch (err) {
      console.error("Failed to load resumes:", err);
    }
    setLoaded(true);
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      await api.post("/api/resumes/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await fetchResumes();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Upload failed");
    }
    setUploading(false);
    e.target.value = "";
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/api/resumes/${id}`);
      setResumes(resumes.filter((r) => r.id !== id));
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  if (!loaded) return null;

  return (
    <div>
      <label className="flex items-center gap-2 cursor-pointer rounded-lg bg-secondary px-4 py-2.5 text-sm font-medium text-secondary-foreground hover:bg-accent transition-colors w-fit">
        <FileUp className="h-4 w-4" />
        {uploading ? "Uploading..." : "Upload PDF Resume"}
        <input
          type="file"
          accept=".pdf"
          onChange={handleUpload}
          disabled={uploading}
          className="hidden"
        />
      </label>
      <p className="text-xs text-muted-foreground mt-1">
        PDF only, max 5MB. Latest upload becomes your primary resume.
      </p>

      {resumes.length > 0 && (
        <div className="mt-3 space-y-2">
          {resumes.map((r) => (
            <div
              key={r.id}
              className="flex items-center justify-between rounded-lg border border-border p-3"
            >
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-foreground">{r.file_name}</span>
                {r.is_primary && (
                  <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                    Primary
                  </span>
                )}
              </div>
              <button
                onClick={() => handleDelete(r.id)}
                className="text-muted-foreground hover:text-destructive transition-colors"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <h2 className="text-lg font-semibold text-card-foreground mb-4">
        {title}
      </h2>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-foreground mb-1">
        {label}
      </label>
      {hint && (
        <p className="text-xs text-muted-foreground mb-1.5">{hint}</p>
      )}
      {children}
    </div>
  );
}

function TagInput({
  tags,
  input,
  setInput,
  onAdd,
  onRemove,
  placeholder,
}: {
  tags: string[];
  input: string;
  setInput: (v: string) => void;
  onAdd: () => void;
  onRemove: (v: string) => void;
  placeholder: string;
}) {
  return (
    <div>
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="flex items-center gap-1 rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-foreground"
            >
              {tag}
              <button
                type="button"
                onClick={() => onRemove(tag)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              onAdd();
            }
          }}
          placeholder={placeholder}
          className="input-field flex-1"
        />
        <button
          type="button"
          onClick={onAdd}
          className="rounded-lg bg-secondary px-3 py-1.5 text-sm text-secondary-foreground hover:bg-accent transition-colors"
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
