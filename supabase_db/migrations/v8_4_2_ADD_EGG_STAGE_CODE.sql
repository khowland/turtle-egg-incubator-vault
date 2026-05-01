-- CR-20260430-194500: Phase 6.2 — Add egg_stage_code column to development_stage
-- This is a transitional column; full UUID migration deferred to CR-20260501-PK-MIGRATION
ALTER TABLE public.development_stage ADD COLUMN IF NOT EXISTS egg_stage_code text;
UPDATE public.development_stage SET egg_stage_code = stage_id WHERE egg_stage_code IS NULL;
