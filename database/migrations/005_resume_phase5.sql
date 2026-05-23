-- Phase 5: Resume Tailoring & Hiring Trends
-- Tables already exist in schema.sql (resumes, resume_tailoring)
-- This migration ensures they're applied if running incrementally.

-- Resumes table (idempotent)
CREATE TABLE IF NOT EXISTS public.resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_url TEXT NOT NULL,
  extracted_text TEXT,
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS resumes_user_id_idx ON public.resumes(user_id);

-- Resume tailoring cache
CREATE TABLE IF NOT EXISTS public.resume_tailoring (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  analysis JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(resume_id, job_id)
);

-- RLS (safe to re-run, will no-op if already enabled)
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resume_tailoring ENABLE ROW LEVEL SECURITY;

-- Policies (drop + create to be idempotent)
DROP POLICY IF EXISTS "Users can view own resumes" ON public.resumes;
CREATE POLICY "Users can view own resumes"
  ON public.resumes FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own resumes" ON public.resumes;
CREATE POLICY "Users can manage own resumes"
  ON public.resumes FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view own tailoring" ON public.resume_tailoring;
CREATE POLICY "Users can view own tailoring"
  ON public.resume_tailoring FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own tailoring" ON public.resume_tailoring;
CREATE POLICY "Users can manage own tailoring"
  ON public.resume_tailoring FOR ALL USING (auth.uid() = user_id);
