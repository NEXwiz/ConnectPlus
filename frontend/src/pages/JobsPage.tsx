import { useState, useEffect, useCallback } from "react";
import { Briefcase, Search, SlidersHorizontal } from "lucide-react";
import JobCard from "@/components/JobCard";
import JobFilters from "@/components/JobFilters";
import SearchBar from "@/components/SearchBar";
import HiringTrends from "@/components/HiringTrends";
import { JobListSkeleton } from "@/components/Skeleton";
import EmptyState from "@/components/EmptyState";
import api from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";
import { useProfileCompletion } from "@/hooks/useProfileCompletion";

interface Job {
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
}

const emptyFilters = {
  employment_type: "",
  role_type: "",
  is_remote: "",
  experience_level: "",
  tech_stack: "",
};

export default function JobsPage() {
  const { user } = useAuth();
  const { isComplete: profileComplete } = useProfileCompletion();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [fitScores, setFitScores] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [searchMode, setSearchMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState(emptyFilters);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const limit = 20;

  // Fetch jobs with current filters
  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number | boolean> = { page, limit };
      if (filters.employment_type) params.employment_type = filters.employment_type;
      if (filters.role_type) params.role_type = filters.role_type;
      if (filters.is_remote) params.is_remote = filters.is_remote === "true";
      if (filters.experience_level) params.experience_level = Number(filters.experience_level);
      if (filters.tech_stack) params.tech_stack = filters.tech_stack;

      const res = await api.get("/api/jobs", { params });
      setJobs(res.data.jobs || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
      setJobs([]);
    }
    setLoading(false);
  }, [page, filters]);

  // Semantic search
  const handleSearch = async (query: string) => {
    setSearching(true);
    setSearchMode(true);
    setSearchQuery(query);
    try {
      const params: Record<string, string | boolean> = { q: query };
      if (filters.employment_type) params.employment_type = filters.employment_type;
      if (filters.role_type) params.role_type = filters.role_type;
      if (filters.is_remote) params.is_remote = filters.is_remote === "true";

      const res = await api.get("/api/jobs/search", { params });
      setJobs(res.data.jobs || []);
    } catch (err) {
      console.error("Search failed:", err);
      setJobs([]);
    }
    setSearching(false);
  };

  const handleClearSearch = () => {
    setSearchMode(false);
    setSearchQuery("");
    fetchJobs();
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const handleClearFilters = () => {
    setFilters(emptyFilters);
    setPage(1);
  };

  useEffect(() => {
    if (!searchMode) {
      fetchJobs();
    } else if (searchQuery) {
      handleSearch(searchQuery);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    if (!user || !profileComplete || jobs.length === 0) return;
    const ids = jobs.map((j) => j.id);
    api.post("/api/jobs/fit/batch", ids).then((res) => {
      setFitScores(res.data);
    }).catch(() => {});
  }, [jobs, user, profileComplete]);

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Briefcase className="h-6 w-6 text-primary" />
        <h1 className="text-2xl font-bold text-foreground">Jobs</h1>
        {!searchMode && (
          <span className="text-sm text-muted-foreground">
            {total} roles available
          </span>
        )}
        {searchMode && (
          <span className="text-sm text-muted-foreground">
            {jobs.length} results for "{searchQuery}"
          </span>
        )}
      </div>

      {/* Search bar */}
      <div className="mb-6 flex gap-2">
        <div className="flex-1">
          <SearchBar
            onSearch={handleSearch}
            onClear={handleClearSearch}
            isSearching={searching}
          />
        </div>
        <button
          onClick={() => setShowMobileFilters(!showMobileFilters)}
          className="lg:hidden flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-accent transition-colors"
          aria-label="Toggle filters"
        >
          <SlidersHorizontal className="h-4 w-4" />
        </button>
      </div>

      {/* Mobile filters */}
      {showMobileFilters && (
        <div className="lg:hidden mb-6 space-y-4">
          <JobFilters
            filters={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
          />
        </div>
      )}

      {/* Layout: filters sidebar + job list */}
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        {/* Sidebar (desktop only) */}
        <aside className="hidden lg:block">
          <div className="sticky top-24 space-y-4 max-h-[calc(100vh-7rem)] overflow-y-auto">
            <JobFilters
              filters={filters}
              onChange={handleFilterChange}
              onClear={handleClearFilters}
            />
            <HiringTrends />
          </div>
        </aside>

        {/* Job list */}
        <div>
          {loading ? (
            <JobListSkeleton />
          ) : jobs.length === 0 ? (
            <EmptyState
              icon={searchMode ? Search : Briefcase}
              title={searchMode ? "No results found" : "No jobs available"}
              description={
                searchMode
                  ? `No jobs matched "${searchQuery}". Try different keywords or clear filters.`
                  : "Try adjusting your filters or check back later for new listings."
              }
              action={searchMode ? { label: "Clear Search", onClick: handleClearSearch } : undefined}
            />
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <JobCard key={job.id} {...job} fitScore={fitScores[job.id]} />
              ))}
            </div>
          )}

          {/* Pagination (only in list mode) */}
          {!searchMode && total > limit && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent disabled:opacity-40"
              >
                Previous
              </button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {Math.ceil(total / limit)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / limit)}
                className="rounded-lg border border-border px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent disabled:opacity-40"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
