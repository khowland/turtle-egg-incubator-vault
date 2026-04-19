-- =============================================================================
-- SQL:        v8_1_0_RESOLUTION_MIGRATION.sql
-- Project:    Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
-- Description: ISS-4 schema alignment, ISS-1 void_reason, hatchling duration,
--              atomic intake RPC (ISS-5). Apply via Supabase SQL editor or CLI.
-- =============================================================================

BEGIN;

-- Mother: align with application intake fields (ISS-4)
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS finder_turtle_name TEXT;
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS intake_condition TEXT;
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS extraction_method TEXT;
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS discovery_location TEXT;
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS carapace_length_mm NUMERIC;

-- Egg: fields used by New Intake / observations
ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS intake_date DATE;
ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS egg_notes TEXT;
ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS last_chalk INTEGER;
ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS last_vasc BOOLEAN;

-- Hatchling analytics (ISS-3 / ISS-4)
ALTER TABLE public.hatchling_ledger ADD COLUMN IF NOT EXISTS incubation_duration_days INTEGER;

-- Hatchling idempotency is enforced in application (select-then-insert/update) so
-- duplicate legacy rows do not block migration.

-- Observation void metadata (ISS-1 soft delete UX)
ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS void_reason TEXT;
UPDATE public.egg_observation SET is_deleted = FALSE WHERE is_deleted IS NULL;

COMMIT;
