-- ============================================================
-- MIGRATION: v9.8.1 — Restrict Clinical SELECT to Authenticated
-- 
-- Previously, SELECT policies allowed 'anon' to read all
-- clinical data. For public deployment, we restrict SELECT
-- to 'authenticated' role. Anon gets no data.
-- ============================================================

-- Drop old policies that allowed anon
DROP POLICY IF EXISTS "bin_select_all" ON public.bin;
DROP POLICY IF EXISTS "bin_obs_select_all" ON public.bin_observation;
DROP POLICY IF EXISTS "egg_select_all" ON public.egg;
DROP POLICY IF EXISTS "egg_obs_select_all" ON public.egg_observation;
DROP POLICY IF EXISTS "intake_select_all" ON public.intake;
DROP POLICY IF EXISTS "hatchling_select_all" ON public.hatchling_ledger;

-- Recreate for authenticated only
CREATE POLICY "bin_select_auth" ON public.bin
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "bin_obs_select_auth" ON public.bin_observation
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "egg_select_auth" ON public.egg
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "egg_obs_select_auth" ON public.egg_observation
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "intake_select_auth" ON public.intake
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "hatchling_select_auth" ON public.hatchling_ledger
    FOR SELECT TO authenticated USING (true);
