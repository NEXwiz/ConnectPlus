-- Supabase Storage Setup for Resumes (MANUAL STEP)
-- ================================================
-- Go to: Supabase Dashboard → Storage → New Bucket
--
-- Bucket name: resumes
-- Public: OFF (private bucket, accessed via signed URLs)
-- File size limit: 5MB
-- Allowed MIME types: application/pdf
--
-- Then add this RLS policy in the SQL Editor:
--
-- Allow authenticated users to upload to their own folder:
CREATE POLICY "Users can upload own resumes"
  ON storage.objects FOR INSERT
  WITH CHECK (
    bucket_id = 'resumes'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Allow users to read their own files:
CREATE POLICY "Users can read own resumes"
  ON storage.objects FOR SELECT
  USING (
    bucket_id = 'resumes'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Allow users to delete their own files:
CREATE POLICY "Users can delete own resumes"
  ON storage.objects FOR DELETE
  USING (
    bucket_id = 'resumes'
    AND auth.uid()::text = (storage.foldername(name))[1]
  );

-- Allow service_role to manage all (backend uses service_role key):
-- This is automatic — service_role bypasses RLS.
