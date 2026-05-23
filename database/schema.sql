-- Connect+ Database Schema
-- Run this in your Supabase SQL Editor to set up all tables.
-- ================================================================

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ================================================================
-- PROFILES (extends Supabase auth.users)
-- ================================================================
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  headline TEXT,
  target_roles TEXT[] DEFAULT '{}',
  github_username TEXT,
  leetcode_username TEXT,
  codeforces_username TEXT,
  profile_completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Auto-create profile on signup via trigger
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email)
  VALUES (NEW.id, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ================================================================
-- JOBS
-- ================================================================
CREATE TABLE public.jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  company TEXT NOT NULL,
  company_logo_url TEXT,
  description TEXT NOT NULL,
  requirements TEXT,
  employment_type TEXT NOT NULL CHECK (
    employment_type IN ('full_time', 'contract', 'freelance', 'government', 'internship')
  ),
  role_type TEXT NOT NULL,
  experience_min INTEGER DEFAULT 0,
  experience_max INTEGER,
  tech_stack TEXT[] DEFAULT '{}',
  location TEXT,
  is_remote BOOLEAN DEFAULT FALSE,
  salary_min INTEGER,
  salary_max INTEGER,
  salary_currency TEXT DEFAULT 'INR',
  apply_url TEXT,
  source TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  embedding VECTOR(1536),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- HNSW index for fast cosine similarity search
CREATE INDEX jobs_embedding_idx ON public.jobs
  USING hnsw (embedding vector_cosine_ops);

-- Standard indexes for filtered queries
CREATE INDEX jobs_employment_type_idx ON public.jobs(employment_type);
CREATE INDEX jobs_role_type_idx ON public.jobs(role_type);
CREATE INDEX jobs_is_active_idx ON public.jobs(is_active);

-- ================================================================
-- GITHUB PROJECTS
-- ================================================================
CREATE TABLE public.github_projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  repo_name TEXT NOT NULL,
  repo_url TEXT NOT NULL,
  description TEXT,
  languages JSONB DEFAULT '{}',
  topics TEXT[] DEFAULT '{}',
  stars INTEGER DEFAULT 0,
  inferred_tech_stack TEXT[] DEFAULT '{}',
  ai_summary TEXT,
  relevance_scores JSONB DEFAULT '{}',
  last_synced_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX github_projects_user_id_idx ON public.github_projects(user_id);

-- ================================================================
-- COMPETITIVE PROGRAMMING PROFILES
-- ================================================================
CREATE TABLE public.cp_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  platform TEXT NOT NULL CHECK (platform IN ('leetcode', 'codeforces')),
  username TEXT NOT NULL,
  rating INTEGER,
  max_rating INTEGER,
  rank TEXT,
  problems_solved INTEGER,
  stats JSONB DEFAULT '{}',
  last_synced_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, platform)
);

-- ================================================================
-- RESUMES
-- ================================================================
CREATE TABLE public.resumes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_url TEXT NOT NULL,
  extracted_text TEXT,
  is_primary BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX resumes_user_id_idx ON public.resumes(user_id);

-- ================================================================
-- RESUME TAILORING CACHE
-- ================================================================
CREATE TABLE public.resume_tailoring (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  resume_id UUID NOT NULL REFERENCES public.resumes(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  analysis JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(resume_id, job_id)
);

-- ================================================================
-- SAVED JOBS
-- ================================================================
CREATE TABLE public.saved_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, job_id)
);

-- ================================================================
-- COMPANIES (future-proofing for company portal)
-- ================================================================
CREATE TABLE public.companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  logo_url TEXT,
  website TEXT,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ================================================================
-- ROW LEVEL SECURITY
-- ================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.github_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resume_tailoring ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;

-- Profiles
CREATE POLICY "Users can view own profile"
  ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile"
  ON public.profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- Jobs: anyone can read active jobs
CREATE POLICY "Anyone can view active jobs"
  ON public.jobs FOR SELECT USING (is_active = true);

-- GitHub projects
CREATE POLICY "Users can view own projects"
  ON public.github_projects FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own projects"
  ON public.github_projects FOR ALL USING (auth.uid() = user_id);

-- CP profiles
CREATE POLICY "Users can view own cp profiles"
  ON public.cp_profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own cp profiles"
  ON public.cp_profiles FOR ALL USING (auth.uid() = user_id);

-- Resumes
CREATE POLICY "Users can view own resumes"
  ON public.resumes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own resumes"
  ON public.resumes FOR ALL USING (auth.uid() = user_id);

-- Resume tailoring
CREATE POLICY "Users can view own tailoring"
  ON public.resume_tailoring FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own tailoring"
  ON public.resume_tailoring FOR ALL USING (auth.uid() = user_id);

-- Saved jobs
CREATE POLICY "Users can view own saved jobs"
  ON public.saved_jobs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own saved jobs"
  ON public.saved_jobs FOR ALL USING (auth.uid() = user_id);

-- ================================================================
-- SEMANTIC SEARCH FUNCTION
-- ================================================================
CREATE OR REPLACE FUNCTION match_jobs(
  query_embedding VECTOR(1536),
  match_threshold FLOAT DEFAULT 0.5,
  match_count INT DEFAULT 20
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  company TEXT,
  company_logo_url TEXT,
  description TEXT,
  employment_type TEXT,
  role_type TEXT,
  tech_stack TEXT[],
  experience_min INT,
  experience_max INT,
  location TEXT,
  is_remote BOOLEAN,
  salary_min INT,
  salary_max INT,
  salary_currency TEXT,
  apply_url TEXT,
  created_at TIMESTAMPTZ,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    j.id, j.title, j.company, j.company_logo_url, j.description,
    j.employment_type, j.role_type, j.tech_stack,
    j.experience_min, j.experience_max, j.location, j.is_remote,
    j.salary_min, j.salary_max, j.salary_currency, j.apply_url,
    j.created_at,
    1 - (j.embedding <=> query_embedding) AS similarity
  FROM public.jobs j
  WHERE j.is_active = true
    AND 1 - (j.embedding <=> query_embedding) > match_threshold
  ORDER BY j.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ================================================================
-- UPDATED_AT TRIGGER
-- ================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER jobs_updated_at
  BEFORE UPDATE ON public.jobs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
