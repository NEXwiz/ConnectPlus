-- Phase 3 Migration: Deep Profile Modeling
-- Run this in Supabase SQL Editor after schema.sql
-- ================================================================

-- -> new columns for skills, preferences, strengths
ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS primary_skills TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS secondary_skills TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS skill_experience JSONB DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS preferred_employment_types TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS preferred_locations TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS salary_min INTEGER,
  ADD COLUMN IF NOT EXISTS salary_max INTEGER,
  ADD COLUMN IF NOT EXISTS salary_currency TEXT DEFAULT 'INR',
  ADD COLUMN IF NOT EXISTS open_to_remote BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS strengths TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS areas_to_improve TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS bio TEXT;

-- -> skill_experience stores per-skill years like: {"Python": 3, "React": 2}
-- -> strengths/areas_to_improve are self-assessed free-text arrays

-- -> update profile_completed logic: now requires more fields
-- -> this function checks if the minimum fields are filled
CREATE OR REPLACE FUNCTION public.check_profile_completion(profile_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
  p RECORD;
BEGIN
  SELECT * INTO p FROM public.profiles WHERE id = profile_id;
  IF NOT FOUND THEN RETURN FALSE; END IF;

  RETURN (
    p.full_name IS NOT NULL AND p.full_name != '' AND
    array_length(p.target_roles, 1) > 0 AND
    array_length(p.primary_skills, 1) > 0 AND
    p.experience_years > 0
  );
END;
$$ LANGUAGE plpgsql;
