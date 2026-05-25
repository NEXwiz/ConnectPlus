-- Add source_id column for deduplication of external job sources
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS source_id TEXT;
CREATE INDEX IF NOT EXISTS idx_jobs_source_source_id ON jobs(source, source_id);
