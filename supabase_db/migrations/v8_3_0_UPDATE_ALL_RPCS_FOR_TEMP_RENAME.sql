-- =============================================================================
-- SQL:        v8_3_0_UPDATE_ALL_RPCS_FOR_TEMP_RENAME.sql
-- CR:         CR-20260430-194500: Consolidate RPC updates for temperature column rename
-- Phase:      1.0: Update all RPCs to use incubator_temp_f, remove temperature from bin
-- Date:       2026-05-01
-- =============================================================================
-- Summary of changes:
--   vault_finalize_intake:       Remove incubator_temp_c from bin INSERT, rename to incubator_temp_f in bin_observation
--   vault_admin_restore:         Remove incubator_temp_c from bin INSERTs, rename to incubator_temp_f in bin_observation INSERTs
--   vault_supplemental_intake:   Remove incubator_temp_c from bin INSERT, rename to incubator_temp_f in bin_observation INSERT
--   vault_finalize_batch_observation: No changes (no temperature references)
--   vault_export_full_backup:    No changes (SELECT * queries only)
-- =============================================================================

-- =============================================================================
-- 1. vault_finalize_intake
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_finalize_intake(p_payload jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $function$
DECLARE
  v_species_id text;
  v_next_intake int;
  v_intake_date date;
  v_session_id text;
  v_observer_id uuid;
  v_intake_id text;
  v_bin jsonb;
  v_bin_id text;
  v_notes text;
  v_egg_count int;
  v_i int;
  v_egg_id text;
  v_eggs_in_bin int;
  v_first_bin text;
BEGIN
  v_species_id := p_payload->>'species_id';
  v_intake_date := (p_payload->>'intake_date')::date;
  v_session_id := p_payload->>'session_id';
  v_observer_id := (p_payload->>'observer_id')::uuid;

  IF v_species_id IS NULL OR v_session_id IS NULL OR v_observer_id IS NULL THEN
    RAISE EXCEPTION 'vault_finalize_intake: missing required payload fields';
  END IF;

  -- Atomic Lock & Increment (§35.5 - Fixes Race Condition)
  SELECT intake_count INTO v_next_intake FROM public.species WHERE species_id = v_species_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'vault_finalize_intake: species_id % not found', v_species_id;
  END IF;
  
  v_next_intake := v_next_intake + 1;
  UPDATE public.species SET intake_count = v_next_intake WHERE species_id = v_species_id;

  -- Requirement §35: Generate Unique Clinical Identifier
  v_intake_id := 'I' || to_char(clock_timestamp(), 'YYYYMMDDHH24MS');

  INSERT INTO public.intake (
    intake_id,
    intake_name,
    finder_turtle_name,
    species_id,
    intake_date,
    intake_condition,
    extraction_method,
    discovery_location,
    mother_weight_g,
    days_in_care,
    clinical_metadata,
    session_id,
    created_by_id,
    modified_by_id
  ) VALUES (
    v_intake_id,
    NULLIF(p_payload#>>'{intake,intake_name}', ''),
    NULLIF(p_payload#>>'{intake,finder_turtle_name}', ''),
    COALESCE(NULLIF(p_payload#>>'{intake,species_id}', '')::text, v_species_id),
    COALESCE(NULLIF(p_payload#>>'{intake,intake_date}', '')::date, v_intake_date),
    NULLIF(p_payload#>>'{intake,intake_condition}', ''),
    NULLIF(p_payload#>>'{intake,extraction_method}', ''),
    NULLIF(p_payload#>>'{intake,discovery_location}', ''),
    NULLIF(p_payload#>>'{intake,mother_weight_g}', '')::numeric,
    (p_payload#>>'{intake,days_in_care}')::int,
    COALESCE((p_payload#>>'{intake,clinical_metadata}')::jsonb, '{}'::jsonb),
    v_session_id,
    v_observer_id,
    v_observer_id
  );

  v_first_bin := NULL;
  FOR v_bin IN SELECT * FROM jsonb_array_elements(COALESCE(p_payload->'bins', '[]'::jsonb))
  LOOP
    v_bin_id := v_bin->>'bin_id';
    v_notes := COALESCE(v_bin->>'bin_notes', 'Clinical Intake Baseline');
    v_egg_count := COALESCE((v_bin->>'egg_count')::int, 0);
    
    IF v_bin_id IS NULL OR v_egg_count < 1 THEN
      RAISE EXCEPTION 'vault_finalize_intake: invalid bin entry (must have 1+ eggs)';
    END IF;

    IF v_first_bin IS NULL THEN
      v_first_bin := v_bin_id;
    END IF;

    -- CR-20260430-194500: Removed incubator_temp_c column from bin INSERT (bin table no longer stores temperature)
    INSERT INTO public.bin (
      bin_id, 
      intake_id, 
      bin_notes, 
      total_eggs,
      target_total_weight_g,
      substrate,
      shelf_location,
      session_id, 
      created_by_id, 
      modified_by_id
    ) VALUES (
      v_bin_id, 
      v_intake_id, 
      v_notes, 
      v_egg_count,
      (v_bin->>'bin_weight_g')::numeric,
      v_bin->>'substrate',
      v_bin->>'shelf_location',
      v_session_id, 
      v_observer_id, 
      v_observer_id
    );

    -- Create Baseline Bin Observation (§2 Compliance)
    -- CR-20260430-194500: Renamed incubator_temp_c to incubator_temp_f
    INSERT INTO public.bin_observation (
      bin_observation_id,
      session_id,
      bin_id,
      observer_id,
      bin_weight_g,
      incubator_temp_f,
      env_notes,
      created_by_id,
      modified_by_id
    ) VALUES (
      'BO-' || v_bin_id || '-' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS'),
      v_session_id,
      v_bin_id,
      v_observer_id,
      (v_bin->>'bin_weight_g')::numeric,
      (v_bin->>'incubator_temp_f')::numeric,
      'Initial Clinical Intake Baseline',
      v_observer_id,
      v_observer_id
    );

    SELECT count(*)::int INTO v_eggs_in_bin FROM public.egg WHERE bin_id = v_bin_id;
    FOR v_i IN 1..v_egg_count LOOP
      v_egg_id := v_bin_id || '-E' || (v_eggs_in_bin + v_i);
      INSERT INTO public.egg (
        egg_id, bin_id, status, current_stage, intake_date,
        session_id, created_by_id, modified_by_id
      ) VALUES (
        v_egg_id, v_bin_id, 'Active', 'S1', v_intake_date,
        v_session_id, v_observer_id, v_observer_id
      );
      INSERT INTO public.egg_observation (
        session_id, egg_id, bin_id, observer_id,
        created_by_id, modified_by_id,
        stage_at_observation, observation_notes, is_deleted
      ) VALUES (
        v_session_id, v_egg_id, v_bin_id, v_observer_id,
        v_observer_id, v_observer_id,
        'S1', 'Clinical Intake Baseline', FALSE
      );
    END LOOP;

  END LOOP;

  RETURN jsonb_build_object(
    'intake_id', v_intake_id,
    'first_bin_id', v_first_bin
  );
END;
$function$;

-- Streamlit uses service role; restrict execute to service_role only.
GRANT EXECUTE ON FUNCTION public.vault_finalize_intake(jsonb) TO service_role;


-- =============================================================================
-- 2. vault_admin_restore (V2 from CR-20260426-145540)
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_admin_restore(p_state_id INT, p_session_id TEXT, p_observer_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_sn_id text := 'SN';  -- Common Snapping Turtle
    v_pa_id text := 'PA';  -- Painted Turtle
    v_bl_id text := 'BL';  -- Blanding's Turtle
BEGIN
    IF p_state_id NOT IN (1, 2) THEN
        RAISE EXCEPTION 'Invalid State ID. Must be 1 (Clean) or 2 (Mid-Season).';
    END IF;

    -- Always log intent before obliteration
    INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
    VALUES (p_session_id, 'CRITICAL', 'Admin Restore Initiated', jsonb_build_object('target_state', p_state_id, 'observer_id', p_observer_id), now());

    -- TRUNCATE all transactional data, preserve lookup tables
    TRUNCATE TABLE public.intake, public.bin, public.egg, public.bin_observation, public.egg_observation, public.hatchling_ledger CASCADE;

    -- ==========================================================================
    -- STATE 1: CLEAN DEPLOYMENT
    -- Guarantee lookup tables are fully seeded (idempotent upserts).
    -- Transactional tables are empty after TRUNCATE above.
    -- ==========================================================================
    IF p_state_id = 1 THEN
        -- Ensure species registry is populated
        INSERT INTO public.species (species_id, species_code, common_name, scientific_name, intake_count)
        VALUES
            ('BL', 'BL', 'Blanding''s Turtle',   'Emydoidea blandingii',     0),
            ('WT', 'WT', 'Wood Turtle',           'Glyptemys insculpta',       0),
            ('OB', 'OB', 'Ornate Box Turtle',     'Terrapene ornata',          0),
            ('PA', 'PA', 'Painted Turtle',        'Chrysemys picta',           0),
            ('SN', 'SN', 'Common Snapping Turtle','Chelydra serpentina',       0),
            ('MT', 'MT', 'Map Turtle',            'Graptemys geographica',     0),
            ('FM', 'FM', 'False Map Turtle',      'Graptemys pseudogeographica',0),
            ('OM', 'OM', 'Ouachita Map Turtle',   'Graptemys ouachitensis',    0),
            ('SS', 'SS', 'Smooth Softshell',      'Apalone mutica',            0),
            ('SM', 'SM', 'Spiny Softshell',       'Apalone spinifera',         0),
            ('MK', 'MK', 'Musk Turtle',           'Sternotherus odoratus',     0)
        ON CONFLICT (species_id) DO UPDATE
            SET common_name = EXCLUDED.common_name,
                scientific_name = EXCLUDED.scientific_name,
                intake_count = 0;

        -- Ensure system_config is present
        INSERT INTO public.system_config (config_key, config_value, description)
        VALUES
            ('APP_VERSION', 'v9.0.0', 'Application version string'),
            ('MIN_EXPORT_STAGE_ORDINAL', '620', 'Minimum stage ordinal for site export')
        ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value;

        INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
        VALUES (p_session_id, 'CRITICAL', 'Admin Restore Completed: State 1 (Clean)', '{}'::jsonb, now());
        RETURN;
    END IF;

    -- ==========================================================================
    -- STATE 2: MID-SEASON TEST SEED
    -- Provides a representative clinical dataset exercising all screens:
    --   - Active eggs at multiple stages (S1, S3, S4, S5)
    --   - Dead eggs (for Deceased/Nonviable dashboard metric)
    --   - Transferred eggs + hatchling_ledger (for Hatched/Transferred metric)
    --   - bin_observation records (Hydration Gate is pre-cleared for this session)
    --   - egg_observation records with realistic stage progression
    --   - Compliant bin IDs using species_code + intake_num + finder + bin_num format
    -- ==========================================================================
    IF p_state_id = 2 THEN

        -- Reset intake counters for test species
        UPDATE public.species SET intake_count = 0
        WHERE species_id IN (v_sn_id, v_pa_id, v_bl_id);

        -- -----------------------------------------------------------------------
        -- INTAKE 1: Common Snapping Turtle — Active mid-season bin (S3 stage)
        --           Bin ID: SN1-HOWLAND-1
        -- -----------------------------------------------------------------------
        UPDATE public.species SET intake_count = 1 WHERE species_id = v_sn_id;

        INSERT INTO public.intake (
            intake_id, intake_name, finder_turtle_name, species_id, intake_date,
            intake_condition, extraction_method, discovery_location,
            mother_weight_g, days_in_care,
            session_id, created_by_id, modified_by_id
        ) VALUES (
            'I-TEST-SN1', '2026-0001', 'Howland', v_sn_id,
            CURRENT_DATE - INTERVAL '18 days',
            'Alive', 'Natural', 'Roadside, CR-12',
            NULL, 2,
            p_session_id, p_observer_id, p_observer_id
        );

        -- CR-20260430-194500: Removed incubator_temp_c column from bin INSERT
        INSERT INTO public.bin (
            bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g,
            substrate, shelf_location, session_id, created_by_id, modified_by_id
        ) VALUES (
            'SN1-HOWLAND-1', 'I-TEST-SN1', 'Primary clutch — active development', 4, 210.0,
            'Vermiculite', 'A1', p_session_id, p_observer_id, p_observer_id
        );

        -- Eggs: 3 active (S3), 1 dead (S2)
        INSERT INTO public.egg (egg_id, bin_id, status, current_stage, intake_date, session_id, created_by_id, modified_by_id) VALUES
            ('SN1-HOWLAND-1-E1', 'SN1-HOWLAND-1', 'Active', 'S3', CURRENT_DATE - INTERVAL '18 days', p_session_id, p_observer_id, p_observer_id),
            ('SN1-HOWLAND-1-E2', 'SN1-HOWLAND-1', 'Active', 'S3', CURRENT_DATE - INTERVAL '18 days', p_session_id, p_observer_id, p_observer_id),
            ('SN1-HOWLAND-1-E3', 'SN1-HOWLAND-1', 'Active', 'S3', CURRENT_DATE - INTERVAL '18 days', p_session_id, p_observer_id, p_observer_id),
            ('SN1-HOWLAND-1-E4', 'SN1-HOWLAND-1', 'Dead',   'S2', CURRENT_DATE - INTERVAL '18 days', p_session_id, p_observer_id, p_observer_id);

        -- Bin observation (pre-clears Hydration Gate for this session)
        -- CR-20260430-194500: Renamed incubator_temp_c to incubator_temp_f
        INSERT INTO public.bin_observation (
            bin_observation_id, session_id, bin_id, observer_id,
            bin_weight_g, incubator_temp_f, env_notes, created_by_id, modified_by_id
        ) VALUES
            ('BO-SN1-HOWLAND-1-BASELINE', p_session_id, 'SN1-HOWLAND-1', p_observer_id,
             200.0, 82.0, 'Intake baseline weight', p_observer_id, p_observer_id),
            ('BO-SN1-HOWLAND-1-CHECK1', p_session_id, 'SN1-HOWLAND-1', p_observer_id,
             209.5, 82.0, 'Mid-season check — nominal moisture retention', p_observer_id, p_observer_id);

        -- Egg observations: S1 baseline → S2 → S3 progression
        INSERT INTO public.egg_observation (
            session_id, egg_id, bin_id, observer_id,
            stage_at_observation, vascularity, chalking, observation_notes, is_deleted,
            created_by_id, modified_by_id
        ) VALUES
            -- E1 progression
            (p_session_id, 'SN1-HOWLAND-1-E1', 'SN1-HOWLAND-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'SN1-HOWLAND-1-E1', 'SN1-HOWLAND-1', p_observer_id, 'S2', FALSE, 1, 'Small chalk spot visible at apex', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'SN1-HOWLAND-1-E1', 'SN1-HOWLAND-1', p_observer_id, 'S3', TRUE,  1, 'Vascularity confirmed', FALSE, p_observer_id, p_observer_id),
            -- E2 progression
            (p_session_id, 'SN1-HOWLAND-1-E2', 'SN1-HOWLAND-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'SN1-HOWLAND-1-E2', 'SN1-HOWLAND-1', p_observer_id, 'S3', TRUE,  1, 'Rapid advancement noted', FALSE, p_observer_id, p_observer_id),
            -- E3 progression
            (p_session_id, 'SN1-HOWLAND-1-E3', 'SN1-HOWLAND-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'SN1-HOWLAND-1-E3', 'SN1-HOWLAND-1', p_observer_id, 'S3', TRUE,  0, 'Vascularity confirmed, no chalk', FALSE, p_observer_id, p_observer_id),
            -- E4 (dead) — S1 baseline only
            (p_session_id, 'SN1-HOWLAND-1-E4', 'SN1-HOWLAND-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'SN1-HOWLAND-1-E4', 'SN1-HOWLAND-1', p_observer_id, 'S2', FALSE, 0, 'Collapse detected — nonviable', FALSE, p_observer_id, p_observer_id);

        -- -----------------------------------------------------------------------
        -- INTAKE 2: Painted Turtle — Advanced bin with S5 pipping + 1 dead egg
        --           Bin ID: PA1-SMITH-1
        -- -----------------------------------------------------------------------
        UPDATE public.species SET intake_count = 1 WHERE species_id = v_pa_id;

        INSERT INTO public.intake (
            intake_id, intake_name, finder_turtle_name, species_id, intake_date,
            intake_condition, extraction_method, discovery_location,
            mother_weight_g, days_in_care,
            session_id, created_by_id, modified_by_id
        ) VALUES (
            'I-TEST-PA1', '2026-0002', 'Smith', v_pa_id,
            CURRENT_DATE - INTERVAL '35 days',
            'Alive', 'Natural', 'Wetland edge, Hwy 14',
            NULL, 1,
            p_session_id, p_observer_id, p_observer_id
        );

        -- CR-20260430-194500: Removed incubator_temp_c column from bin INSERT
        INSERT INTO public.bin (
            bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g,
            substrate, shelf_location, session_id, created_by_id, modified_by_id
        ) VALUES (
            'PA1-SMITH-1', 'I-TEST-PA1', 'Advanced clutch — pipping imminent', 3, 95.0,
            'Vermiculite', 'B1', p_session_id, p_observer_id, p_observer_id
        );

        -- Eggs: 2 active (S4, S5), 1 dead
        INSERT INTO public.egg (egg_id, bin_id, status, current_stage, intake_date, session_id, created_by_id, modified_by_id) VALUES
            ('PA1-SMITH-1-E1', 'PA1-SMITH-1', 'Active', 'S5', CURRENT_DATE - INTERVAL '35 days', p_session_id, p_observer_id, p_observer_id),
            ('PA1-SMITH-1-E2', 'PA1-SMITH-1', 'Active', 'S4', CURRENT_DATE - INTERVAL '35 days', p_session_id, p_observer_id, p_observer_id),
            ('PA1-SMITH-1-E3', 'PA1-SMITH-1', 'Dead',   'S3', CURRENT_DATE - INTERVAL '35 days', p_session_id, p_observer_id, p_observer_id);

        -- CR-20260430-194500: Renamed incubator_temp_c to incubator_temp_f
        INSERT INTO public.bin_observation (
            bin_observation_id, session_id, bin_id, observer_id,
            bin_weight_g, incubator_temp_f, env_notes, created_by_id, modified_by_id
        ) VALUES
            ('BO-PA1-SMITH-1-BASELINE', p_session_id, 'PA1-SMITH-1', p_observer_id,
             90.0, 82.0, 'Intake baseline', p_observer_id, p_observer_id),
            ('BO-PA1-SMITH-1-CHECK1', p_session_id, 'PA1-SMITH-1', p_observer_id,
             94.5, 82.0, '2ml water added', p_observer_id, p_observer_id);

        INSERT INTO public.egg_observation (
            session_id, egg_id, bin_id, observer_id,
            stage_at_observation, vascularity, chalking, observation_notes, is_deleted,
            created_by_id, modified_by_id
        ) VALUES
            (p_session_id, 'PA1-SMITH-1-E1', 'PA1-SMITH-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'PA1-SMITH-1-E1', 'PA1-SMITH-1', p_observer_id, 'S3', TRUE, 1, 'Vascularity strong', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'PA1-SMITH-1-E1', 'PA1-SMITH-1', p_observer_id, 'S5', TRUE, 2, 'Pipping initiated — monitor closely', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'PA1-SMITH-1-E2', 'PA1-SMITH-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'PA1-SMITH-1-E2', 'PA1-SMITH-1', p_observer_id, 'S4', TRUE, 1, 'C-stage shadow visible', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'PA1-SMITH-1-E3', 'PA1-SMITH-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'PA1-SMITH-1-E3', 'PA1-SMITH-1', p_observer_id, 'S3', FALSE, 0, 'Mold detected on surface', FALSE, p_observer_id, p_observer_id);

        -- -----------------------------------------------------------------------
        -- INTAKE 3: Blanding's Turtle — Completed clutch (hatched + ledger)
        --           Bin ID: BL1-JONES-1 — exercises Hatched/Transferred metric
        -- -----------------------------------------------------------------------
        UPDATE public.species SET intake_count = 1 WHERE species_id = v_bl_id;

        INSERT INTO public.intake (
            intake_id, intake_name, finder_turtle_name, species_id, intake_date,
            intake_condition, extraction_method, discovery_location,
            mother_weight_g, days_in_care,
            session_id, created_by_id, modified_by_id
        ) VALUES (
            'I-TEST-BL1', '2026-0003', 'Jones', v_bl_id,
            CURRENT_DATE - INTERVAL '60 days',
            'Alive', 'Surgery', 'Suburban pond, rescued',
            NULL, 3,
            p_session_id, p_observer_id, p_observer_id
        );

        -- CR-20260430-194500: Removed incubator_temp_c column from bin INSERT
        INSERT INTO public.bin (
            bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g,
            substrate, shelf_location, session_id, created_by_id, modified_by_id
        ) VALUES (
            'BL1-JONES-1', 'I-TEST-BL1', 'Season-complete clutch — ready for retirement', 3, 80.0,
            'Perlite', 'C1', p_session_id, p_observer_id, p_observer_id
        );

        -- Eggs: 2 transferred (S6), 1 still active (S5)
        INSERT INTO public.egg (egg_id, bin_id, status, current_stage, intake_date, session_id, created_by_id, modified_by_id) VALUES
            ('BL1-JONES-1-E1', 'BL1-JONES-1', 'Transferred', 'S6', CURRENT_DATE - INTERVAL '60 days', p_session_id, p_observer_id, p_observer_id),
            ('BL1-JONES-1-E2', 'BL1-JONES-1', 'Transferred', 'S6', CURRENT_DATE - INTERVAL '60 days', p_session_id, p_observer_id, p_observer_id),
            ('BL1-JONES-1-E3', 'BL1-JONES-1', 'Active',      'S5', CURRENT_DATE - INTERVAL '60 days', p_session_id, p_observer_id, p_observer_id);

        -- CR-20260430-194500: Renamed incubator_temp_c to incubator_temp_f
        INSERT INTO public.bin_observation (
            bin_observation_id, session_id, bin_id, observer_id,
            bin_weight_g, incubator_temp_f, env_notes, created_by_id, modified_by_id
        ) VALUES
            ('BO-BL1-JONES-1-BASELINE', p_session_id, 'BL1-JONES-1', p_observer_id,
             78.0, 82.0, 'Intake baseline', p_observer_id, p_observer_id),
            ('BO-BL1-JONES-1-FINAL', p_session_id, 'BL1-JONES-1', p_observer_id,
             79.5, 82.0, 'Pre-hatch check', p_observer_id, p_observer_id);

        INSERT INTO public.egg_observation (
            session_id, egg_id, bin_id, observer_id,
            stage_at_observation, vascularity, chalking, observation_notes, is_deleted,
            created_by_id, modified_by_id
        ) VALUES
            (p_session_id, 'BL1-JONES-1-E1', 'BL1-JONES-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'BL1-JONES-1-E1', 'BL1-JONES-1', p_observer_id, 'S5', TRUE, 2, 'Pipping observed', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'BL1-JONES-1-E1', 'BL1-JONES-1', p_observer_id, 'S6', TRUE, 3, 'Hatched — transferred to rearing tub', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'BL1-JONES-1-E2', 'BL1-JONES-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'BL1-JONES-1-E2', 'BL1-JONES-1', p_observer_id, 'S6', TRUE, 3, 'Hatched — transferred to rearing tub', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'BL1-JONES-1-E3', 'BL1-JONES-1', p_observer_id, 'S1', FALSE, 0, 'Intake baseline', FALSE, p_observer_id, p_observer_id),
            (p_session_id, 'BL1-JONES-1-E3', 'BL1-JONES-1', p_observer_id, 'S5', TRUE, 1, 'Pipping initiated', FALSE, p_observer_id, p_observer_id);

        -- Hatchling ledger for the two transferred eggs
        INSERT INTO public.hatchling_ledger (
            egg_id, intake_id, hatch_date, vitality_score, incubation_duration_days,
            notes, session_id, created_by_id, modified_by_id
        ) VALUES
            ('BL1-JONES-1-E1', 'I-TEST-BL1', CURRENT_DATE - INTERVAL '2 days', 'A - Excellent', 58,
             'Synthetic S6 seed — CR-20260426', p_session_id, p_observer_id, p_observer_id),
            ('BL1-JONES-1-E2', 'I-TEST-BL1', CURRENT_DATE - INTERVAL '2 days', 'A - Excellent', 58,
             'Synthetic S6 seed — CR-20260426', p_session_id, p_observer_id, p_observer_id);

        INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
        VALUES (p_session_id, 'CRITICAL', 'Admin Restore Completed: State 2 (Mid-Season v2 — CR-20260426)', '{}'::jsonb, now());
    END IF;
END;
$$;

GRANT EXECUTE ON FUNCTION public.vault_admin_restore(INT, TEXT, UUID) TO service_role;


-- =============================================================================
-- 3. vault_supplemental_intake
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_supplemental_intake(p_payload jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$ 
DECLARE
  v_intake_id text;
  v_session_id text;
  v_observer_id uuid;
  v_supp_date date;
  v_orig_intake_date date;
  v_bin jsonb;
  v_bin_id text;
  v_new_egg_count int;
  v_is_new_bin boolean;
  v_current_eggs int;
  v_i int;
  v_egg_id text;
  v_first_bin text := NULL;
  v_bin_record record;
BEGIN
  v_intake_id := p_payload->>'intake_id';
  v_session_id := p_payload->>'session_id';
  v_observer_id := (p_payload->>'observer_id')::uuid;
  v_supp_date := (p_payload->>'supplemental_date')::date;

  -- 1. Validate Intake Exists & Date
  SELECT intake_date INTO v_orig_intake_date FROM public.intake WHERE intake_id = v_intake_id;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Supplemental Intake failed: Intake ID % not found.', v_intake_id;
  END IF;

  IF v_supp_date < v_orig_intake_date THEN
    RAISE EXCEPTION 'Temporal Paradox: Supplemental date (%) cannot be before original intake date (%).', v_supp_date, v_orig_intake_date;
  END IF;

  -- 2. Process Bins
  FOR v_bin IN SELECT * FROM jsonb_array_elements(COALESCE(p_payload->'bins', '[]'::jsonb))
  LOOP
    v_bin_id := v_bin->>'bin_id';
    v_new_egg_count := COALESCE((v_bin->>'new_egg_count')::int, 0);
    v_is_new_bin := COALESCE((v_bin->>'is_new_bin')::boolean, false);

    IF v_new_egg_count < 1 THEN
      CONTINUE; -- Skip if no new eggs to add
    END IF;

    IF v_first_bin IS NULL THEN
      v_first_bin := v_bin_id;
    END IF;

    IF v_is_new_bin THEN
      -- Create brand new bin
      -- CR-20260430-194500: Removed incubator_temp_c from bin INSERT
      INSERT INTO public.bin (
        bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g,
        substrate, shelf_location, session_id, created_by_id, modified_by_id
      ) VALUES (
        v_bin_id, v_intake_id, COALESCE(v_bin->>'notes', 'Supplemental Bin'), v_new_egg_count,
        (v_bin->>'mass')::numeric, v_bin->>'substrate', v_bin->>'shelf',
        v_session_id, v_observer_id, v_observer_id
      );

      -- Baseline Bin Observation
      -- CR-20260430-194500: Renamed incubator_temp_c to incubator_temp_f
      INSERT INTO public.bin_observation (
        bin_observation_id, session_id, bin_id, observer_id, bin_weight_g, incubator_temp_f, env_notes, created_by_id, modified_by_id
      ) VALUES (
        'BO-' || v_bin_id || '-' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS'),
        v_session_id, v_bin_id, v_observer_id, (v_bin->>'mass')::numeric, (v_bin->>'temp')::numeric, 'Supplemental Baseline', v_observer_id, v_observer_id
      );

      v_current_eggs := 0;
    ELSE
      -- Add to existing bin
      -- Lock the bin record to prevent race conditions
      SELECT * INTO v_bin_record FROM public.bin WHERE bin_id = v_bin_id FOR UPDATE;
      IF NOT FOUND THEN
        RAISE EXCEPTION 'Supplemental Intake failed: Bin ID % not found.', v_bin_id;
      END IF;

      -- Update the bin's total_eggs count
      UPDATE public.bin SET total_eggs = total_eggs + v_new_egg_count WHERE bin_id = v_bin_id;

      -- Get current max egg number (safely locked via bin)
      SELECT count(*) INTO v_current_eggs FROM public.egg WHERE bin_id = v_bin_id;
    END IF;

    -- Generate Eggs
    FOR v_i IN 1..v_new_egg_count LOOP
      v_egg_id := v_bin_id || '-E' || (v_current_eggs + v_i);

      INSERT INTO public.egg (
        egg_id, bin_id, status, current_stage, intake_date, session_id, created_by_id, modified_by_id
      ) VALUES (
        v_egg_id, v_bin_id, 'Active', 'S1', v_supp_date, v_session_id, v_observer_id, v_observer_id
      );

      INSERT INTO public.egg_observation (
        session_id, egg_id, bin_id, observer_id, created_by_id, modified_by_id,
        stage_at_observation, observation_notes, is_deleted
      ) VALUES (
        v_session_id, v_egg_id, v_bin_id, v_observer_id, v_observer_id, v_observer_id,
        'S1', 'Supplemental Intake Baseline', FALSE
      );
    END LOOP;

  END LOOP;

  RETURN jsonb_build_object(
    'intake_id', v_intake_id,
    'first_bin_id', COALESCE(v_first_bin, 'NONE')
  );
END;
$$;

GRANT EXECUTE ON FUNCTION public.vault_supplemental_intake(jsonb) TO service_role;
