-- Phase 4 Migration: GitHub OAuth token storage
-- Run this in Supabase SQL Editor
-- ================================================================

ALTER TABLE public.profiles
  ADD COLUMN IF NOT EXISTS github_access_token TEXT;
