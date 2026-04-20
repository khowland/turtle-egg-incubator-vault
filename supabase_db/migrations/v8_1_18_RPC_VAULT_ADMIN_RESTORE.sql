-- =============================================================================
-- SQL:        v8_1_18_RPC_VAULT_ADMIN_RESTORE.sql
-- Project:    Incubator Vault v8.1.4 — Red Team DB State Architecture
-- Description: Secure RPC for Database State Wipe & Seed (Dead Man's Switch)
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_admin_restore(p_state_id INT, p_session_id TEXT, p_observer_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_species_id text;
BEGIN
    IF p_state_id NOT IN (1, 2) THEN
        RAISE EXCEPTION 'Invalid State ID. Must be 1 (Clean) or 2 (Mid-Season).';
    END IF;

    -- Always Log the intent before obliteration
    INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
    VALUES (p_session_id, 'CRITICAL', 'Admin Restore Initiated', jsonb_build_object('target_state', p_state_id, 'observer_id', p_observer_id), now());

    -- TRUNCATE all transactional data, preserve lookup tables
    TRUNCATE TABLE public.intake, public.bin, public.egg, public.bin_observation, public.egg_observation, public.hatchling_ledger CASCADE;

    -- STATE 1: CLEAN DEPLOYMENT ends here.
    IF p_state_id = 1 THEN
        INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
        VALUES (p_session_id, 'CRITICAL', 'Admin Restore Completed: State 1 (Clean)', '{}'::jsonb, now());
        RETURN;
    END IF;

    -- STATE 2: MID-SEASON SEED
    IF p_state_id = 2 THEN
        -- Explicit assignment to prevent Supabase dashboard parser errors (42P01)
        v_species_id := (SELECT species_id FROM public.species LIMIT 1);
        
        IF v_species_id IS NULL THEN
            RAISE EXCEPTION 'Species lookup table is empty. Cannot seed.';
        END IF;

        -- Seed 1: Active Mid-Season Intake (Synthesized dates via Postgres CURRENT_DATE)
        INSERT INTO public.intake (intake_id, intake_name, finder_turtle_name, species_id, intake_date, session_id, created_by_id, modified_by_id)
        VALUES ('I-TEST-01', 'Mid-Season Active', 'Test Turtle A', v_species_id, CURRENT_DATE - INTERVAL '10 days', p_session_id, p_observer_id, p_observer_id);
        
        INSERT INTO public.bin (bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g, incubator_temp_c, substrate, shelf_location, session_id, created_by_id, modified_by_id)
        VALUES ('B-TEST-01', 'I-TEST-01', 'Mid-Season Active Bin', 2, 100.0, 28.5, 'Vermiculite', 'A1', p_session_id, p_observer_id, p_observer_id);

        INSERT INTO public.egg (egg_id, bin_id, status, current_stage, intake_date, session_id, created_by_id, modified_by_id)
        VALUES ('E-TEST-01-1', 'B-TEST-01', 'Active', 'S4', CURRENT_DATE - INTERVAL '10 days', p_session_id, p_observer_id, p_observer_id),
               ('E-TEST-01-2', 'B-TEST-01', 'Active', 'S5', CURRENT_DATE - INTERVAL '10 days', p_session_id, p_observer_id, p_observer_id);

        -- Seed 2: Hatched Egg (S6) and Ledger Entry
        INSERT INTO public.intake (intake_id, intake_name, finder_turtle_name, species_id, intake_date, session_id, created_by_id, modified_by_id)
        VALUES ('I-TEST-02', 'Mid-Season Hatched', 'Test Turtle B', v_species_id, CURRENT_DATE - INTERVAL '45 days', p_session_id, p_observer_id, p_observer_id);
        
        INSERT INTO public.bin (bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g, incubator_temp_c, substrate, shelf_location, session_id, created_by_id, modified_by_id)
        VALUES ('B-TEST-02', 'I-TEST-02', 'Mid-Season Hatched Bin', 1, 50.0, 28.5, 'Vermiculite', 'A2', p_session_id, p_observer_id, p_observer_id);

        INSERT INTO public.egg (egg_id, bin_id, status, current_stage, intake_date, session_id, created_by_id, modified_by_id)
        VALUES ('E-TEST-02-1', 'B-TEST-02', 'Transferred', 'S6', CURRENT_DATE - INTERVAL '45 days', p_session_id, p_observer_id, p_observer_id);

        INSERT INTO public.hatchling_ledger (egg_id, intake_id, hatch_date, vitality_score, incubation_duration_days, notes, session_id, created_by_id, modified_by_id)
        VALUES ('E-TEST-02-1', 'I-TEST-02', CURRENT_DATE - INTERVAL '1 day', 'A - Excellent', 44, 'Synthetic S6 Seed', p_session_id, p_observer_id, p_observer_id);

        INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
        VALUES (p_session_id, 'CRITICAL', 'Admin Restore Completed: State 2 (Mid-Season)', '{}'::jsonb, now());
    END IF;
END;
$$;

GRANT EXECUTE ON FUNCTION public.vault_admin_restore(INT, TEXT, UUID) TO service_role;
