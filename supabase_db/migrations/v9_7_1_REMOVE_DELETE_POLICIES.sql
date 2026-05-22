-- =============================================================================
-- MIGRATION: v9.7.1 — Remove DELETE Policies from Clinical Tables
-- Author: A0-PM | QA Triad v3 | Sprint 2 — LIVE-3
-- Date: 2026-05-22
-- Requirement: §4 Resilience & Security — Soft Delete Mandate
-- =============================================================================
--
-- Context:
--   v9.7.0 added RLS policies including DELETE policies on all 6 clinical
--   tables. Per §4, clinical data must NEVER be hard-deleted. All deletions
--   must use the soft-delete pattern (UPDATE is_deleted = true).
--
--   Adversarial review by QA Triad hacker subordinate identified this as a
--   HIGH severity gap: any authenticated user could call .delete() and
--   permanently destroy clinical records with zero forensic trace.
--
--   This migration drops all DELETE policies. After this:
--   - anon:         SELECT only
--   - authenticated: SELECT, INSERT, UPDATE (soft-delete via is_deleted)
--   - service_role:  Full access (bypasses RLS — for server-side RPCs only)
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Drop all DELETE policies created in v9.7.0
-- ---------------------------------------------------------------------------

DROP POLICY IF EXISTS "bin_delete_auth" ON public.bin;
DROP POLICY IF EXISTS "bin_obs_delete_auth" ON public.bin_observation;
DROP POLICY IF EXISTS "egg_delete_auth" ON public.egg;
DROP POLICY IF EXISTS "egg_obs_delete_auth" ON public.egg_observation;
DROP POLICY IF EXISTS "intake_delete_auth" ON public.intake;
DROP POLICY IF EXISTS "hatchling_delete_auth" ON public.hatchling_ledger;

-- ---------------------------------------------------------------------------
-- Version Bump
-- ---------------------------------------------------------------------------

UPDATE public.system_config
SET config_value = 'v9.7.1'
WHERE config_name = 'APP_VERSION';

COMMIT;

-- Verification query (run after applying):
-- SELECT tablename, cmd FROM pg_policies
-- WHERE schemaname = 'public'
-- AND cmd = 'DELETE';
-- (should return 0 rows)
