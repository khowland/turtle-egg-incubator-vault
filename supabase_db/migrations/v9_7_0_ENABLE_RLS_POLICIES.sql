-- =============================================================================
-- MIGRATION: v9.7.0 — Enable Row Level Security on Clinical Tables
-- Author: A0-PM | QA Triad v3 | DB-1
-- Date: 2026-05-21
-- Requirement: §4 Resilience & Security
-- =============================================================================
--
-- Context:
--   - Requirements §2.4 mandates Global Clinical Visibility: all active data
--     visible to any authenticated observer.
--   - Requirements §4 mandates Soft Delete via is_deleted flags.
--   - A2-DB audit confirmed zero RLS policies exist. This migration adds them.
--
-- Design:
--   - SELECT: All roles (anon, authenticated) can read clinical data.
--     is_deleted=true rows are visible for forensic auditing per §4.
--   - INSERT/UPDATE/DELETE: Only authenticated role. Anon cannot modify.
--   - service_role: Bypasses all RLS (intended for server-side RPCs only).
--   - Read-only tables (species, observer, system_config, etc.) remain
--     unprotected intentionally — they contain no PII or clinical data.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Enable RLS on Clinical Tables
-- ---------------------------------------------------------------------------

ALTER TABLE public.bin ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bin_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.egg ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.egg_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.intake ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hatchling_ledger ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 2. SELECT Policies — Global Clinical Visibility (§2.4)
--    All roles (anon + authenticated) can read clinical data.
--    This matches the single-facility, single-shift model where all observers
--    share global visibility of active incubation records.
-- ---------------------------------------------------------------------------

-- bin
CREATE POLICY "bin_select_all" ON public.bin
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- bin_observation
CREATE POLICY "bin_obs_select_all" ON public.bin_observation
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- egg
CREATE POLICY "egg_select_all" ON public.egg
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- egg_observation
CREATE POLICY "egg_obs_select_all" ON public.egg_observation
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- intake
CREATE POLICY "intake_select_all" ON public.intake
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- hatchling_ledger
CREATE POLICY "hatchling_select_all" ON public.hatchling_ledger
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- ---------------------------------------------------------------------------
-- 3. INSERT Policies — Authenticated Only
--    Only authenticated observers can create clinical records.
--    Anon key can read but not write.
-- ---------------------------------------------------------------------------

-- bin
CREATE POLICY "bin_insert_auth" ON public.bin
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- bin_observation
CREATE POLICY "bin_obs_insert_auth" ON public.bin_observation
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- egg
CREATE POLICY "egg_insert_auth" ON public.egg
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- egg_observation
CREATE POLICY "egg_obs_insert_auth" ON public.egg_observation
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- intake
CREATE POLICY "intake_insert_auth" ON public.intake
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- hatchling_ledger
CREATE POLICY "hatchling_insert_auth" ON public.hatchling_ledger
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ---------------------------------------------------------------------------
-- 4. UPDATE Policies — Authenticated Only
-- ---------------------------------------------------------------------------

-- bin
CREATE POLICY "bin_update_auth" ON public.bin
    FOR UPDATE
    TO authenticated
    USING (true);

-- bin_observation
CREATE POLICY "bin_obs_update_auth" ON public.bin_observation
    FOR UPDATE
    TO authenticated
    USING (true);

-- egg
CREATE POLICY "egg_update_auth" ON public.egg
    FOR UPDATE
    TO authenticated
    USING (true);

-- egg_observation
CREATE POLICY "egg_obs_update_auth" ON public.egg_observation
    FOR UPDATE
    TO authenticated
    USING (true);

-- intake
CREATE POLICY "intake_update_auth" ON public.intake
    FOR UPDATE
    TO authenticated
    USING (true);

-- hatchling_ledger
CREATE POLICY "hatchling_update_auth" ON public.hatchling_ledger
    FOR UPDATE
    TO authenticated
    USING (true);

-- ---------------------------------------------------------------------------
-- 5. DELETE Policies — Authenticated Only
--    Note: Clinical data is never hard-deleted (§4 Soft Delete).
--    These policies exist for completeness but should never be triggered.
-- ---------------------------------------------------------------------------

-- bin
CREATE POLICY "bin_delete_auth" ON public.bin
    FOR DELETE
    TO authenticated
    USING (true);

-- bin_observation
CREATE POLICY "bin_obs_delete_auth" ON public.bin_observation
    FOR DELETE
    TO authenticated
    USING (true);

-- egg
CREATE POLICY "egg_delete_auth" ON public.egg
    FOR DELETE
    TO authenticated
    USING (true);

-- egg_observation
CREATE POLICY "egg_obs_delete_auth" ON public.egg_observation
    FOR DELETE
    TO authenticated
    USING (true);

-- intake
CREATE POLICY "intake_delete_auth" ON public.intake
    FOR DELETE
    TO authenticated
    USING (true);

-- hatchling_ledger
CREATE POLICY "hatchling_delete_auth" ON public.hatchling_ledger
    FOR DELETE
    TO authenticated
    USING (true);

-- ---------------------------------------------------------------------------
-- 6. Version Bump
-- ---------------------------------------------------------------------------

UPDATE public.system_config
SET config_value = 'v9.7.0'
WHERE config_name = 'APP_VERSION';

COMMIT;

-- Verification queries (run after migration):
-- SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename, cmd;
