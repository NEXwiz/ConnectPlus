-- Phase 6: Growth Roadmaps & Career Intelligence
-- Stores AI-generated learning paths and milestone progress.

CREATE TABLE IF NOT EXISTS public.growth_roadmaps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  target_role TEXT NOT NULL,
  gap_analysis JSONB NOT NULL,        -- {missing_skills[], weak_areas[], strengths[]}
  timeline_weeks INT NOT NULL DEFAULT 12,
  status TEXT NOT NULL DEFAULT 'active', -- active, completed, archived
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS growth_roadmaps_user_id_idx ON public.growth_roadmaps(user_id);

CREATE TABLE IF NOT EXISTS public.roadmap_milestones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  roadmap_id UUID NOT NULL REFERENCES public.growth_roadmaps(id) ON DELETE CASCADE,
  week INT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL DEFAULT 'learn', -- learn, build, practice
  resources JSONB DEFAULT '[]',           -- [{title, url, type}]
  is_completed BOOLEAN DEFAULT FALSE,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS roadmap_milestones_roadmap_id_idx ON public.roadmap_milestones(roadmap_id);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_roadmap_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS roadmap_updated_at ON public.growth_roadmaps;
CREATE TRIGGER roadmap_updated_at
  BEFORE UPDATE ON public.growth_roadmaps
  FOR EACH ROW EXECUTE FUNCTION update_roadmap_timestamp();

-- RLS
ALTER TABLE public.growth_roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.roadmap_milestones ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can manage own roadmaps" ON public.growth_roadmaps;
CREATE POLICY "Users can manage own roadmaps"
  ON public.growth_roadmaps FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own milestones" ON public.roadmap_milestones;
CREATE POLICY "Users can manage own milestones"
  ON public.roadmap_milestones FOR ALL
  USING (roadmap_id IN (SELECT id FROM public.growth_roadmaps WHERE user_id = auth.uid()));
