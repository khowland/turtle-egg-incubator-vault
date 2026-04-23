-- Migration: Add JSONB clinical metadata for analytics
ALTER TABLE public.intake 
ADD COLUMN IF NOT EXISTS clinical_metadata JSONB DEFAULT '{}'::jsonb;
