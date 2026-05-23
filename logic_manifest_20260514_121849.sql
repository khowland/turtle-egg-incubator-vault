-- IMMUTABLE LOGIC MANIFEST
-- Generated: 2026-05-14 12:18:52.381282

-- Function: public.update_modified_column
CREATE OR REPLACE FUNCTION public.update_modified_column()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$function$

;

-- Function: public.generate_intake_id
CREATE OR REPLACE FUNCTION public.generate_intake_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
 BEGIN
     -- Respect existing IDs if provided (essential for our validation runner)
     IF NEW.intake_id IS NULL THEN
         NEW.intake_id := 'I' || REPLACE(COALESCE(NEW.intake_name, 'UNK'), ' ', '') || '_' || 
                          NEW.species_id || '_' || 
                          TO_CHAR(NEW.intake_date, 'YYYYMMDD');
     END IF;
     RETURN NEW;
 END;
 $function$

;

-- Function: public.vault_export_full_backup
CREATE OR REPLACE FUNCTION public.vault_export_full_backup()
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
    v_result jsonb;
BEGIN
    -- Using explicit PL/pgSQL assignment (:=) to prevent Supabase SQL Editor 
    -- from confusing 'SELECT INTO' with table creation/relation errors.
    v_result := jsonb_build_object(
        'intake', (SELECT COALESCE(jsonb_agg(row_to_json(i)), '[]'::jsonb) FROM public.intake i),
        'bin', (SELECT COALESCE(jsonb_agg(row_to_json(b)), '[]'::jsonb) FROM public.bin b),
        'egg', (SELECT COALESCE(jsonb_agg(row_to_json(e)), '[]'::jsonb) FROM public.egg e),
        'bin_observation', (SELECT COALESCE(jsonb_agg(row_to_json(bo)), '[]'::jsonb) FROM public.bin_observation bo),
        'egg_observation', (SELECT COALESCE(jsonb_agg(row_to_json(eo)), '[]'::jsonb) FROM public.egg_observation eo),
        'hatchling_ledger', (SELECT COALESCE(jsonb_agg(row_to_json(hl)), '[]'::jsonb) FROM public.hatchling_ledger hl),
        'system_log', (SELECT COALESCE(jsonb_agg(row_to_json(sl)), '[]'::jsonb) FROM public.system_log sl),
        'timestamp', now()
    );
    
    RETURN v_result;
END;
$function$

;

-- Function: public.vault_finalize_supplemental_bin
CREATE OR REPLACE FUNCTION public.vault_finalize_supplemental_bin(p_intake_id bigint, p_session_id text, p_observer_id bigint, p_observer_name text, p_supp_date date, p_bins jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
BEGIN
    -- Standard Placeholder for Supplemental Logic 
    -- (Actual logic to follow in clinical hardening phase)
    RETURN jsonb_build_object('success', true);
END;
$function$

;

-- Function: public.vault_finalize_intake
CREATE OR REPLACE FUNCTION public.vault_finalize_intake(p_payload jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
DECLARE
  v_species_id bigint;
  v_next_intake int;
  v_intake_date date;
  v_session_token text;
  v_session_id bigint;
  v_observer_id bigint;
  v_observer_name text; -- Added for audit trail
  v_intake_id bigint;
  v_bin jsonb;
  v_bin_code text;
  v_generated_bin_id bigint;
  v_notes text;
  v_egg_count int;
  v_i int;
  v_egg_code text;
  v_numeric_egg_id bigint;
  v_eggs_in_bin int;
  v_first_bin bigint;
BEGIN
  -- 1. Extract & Map Identity (Enterprise Sovereign Layer)
  v_species_id := (p_payload->>'species_id')::bigint;
  v_intake_date := (p_payload->>'intake_date')::date;
  v_session_token := p_payload->>'session_id'; 
  
  -- Map Observer ID and retrieve Name for audit trail
  SELECT o.observer_id, o.display_name 
  INTO v_observer_id, v_observer_name
  FROM public.observer o 
  WHERE o.observer_id = (p_payload->>'observer_id')::bigint;

  -- Requirement Â§4: Map Session Token (UUID string) to Session ID (BIGINT)
  SELECT s.session_id INTO v_session_id 
  FROM public.session_log s 
  WHERE s.session_token = v_session_token 
  LIMIT 1;
  
  IF v_session_id IS NULL THEN
      INSERT INTO public.session_log (session_token, user_name) 
      VALUES (v_session_token, COALESCE(v_observer_name, 'SYSTEM')) 
      RETURNING session_id INTO v_session_id;
  END IF;

  IF v_species_id IS NULL OR v_session_id IS NULL THEN
    RAISE EXCEPTION 'vault_finalize_intake: missing required payload fields';
  END IF;

  -- 2. Biological Lock & Registry Update
  SELECT intake_count INTO v_next_intake FROM public.species WHERE species_id = v_species_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'vault_finalize_intake: species_id % not found', v_species_id;
  END IF;
  
  v_next_intake := v_next_intake + 1;
  UPDATE public.species SET intake_count = v_next_intake WHERE species_id = v_species_id;

  -- 3. Core Intake Ledger (Â§1.6 Identity)
  INSERT INTO public.intake (
    intake_name, finder_turtle_name, species_id, intake_date,
    intake_condition, extraction_method, discovery_location,
    mother_weight_g, days_in_care, clinical_metadata,
    session_id, created_by_id, modified_by_id
  ) VALUES (
    NULLIF(p_payload#>>'{intake,intake_name}', ''),
    NULLIF(p_payload#>>'{intake,finder_turtle_name}', ''),
    v_species_id,
    COALESCE(NULLIF(p_payload#>>'{intake,intake_date}', '')::date, v_intake_date),
    NULLIF(p_payload#>>'{intake,intake_condition}', ''),
    NULLIF(p_payload#>>'{intake,extraction_method}', ''),
    NULLIF(p_payload#>>'{intake,discovery_location}', ''),
    NULLIF(p_payload#>>'{intake,mother_weight_g}', '')::numeric,
    (p_payload#>>'{intake,days_in_care}')::int,
    COALESCE((p_payload#>>'{intake,clinical_metadata}')::jsonb, '{}'::jsonb),
    v_session_id, v_observer_id, v_observer_id
  ) RETURNING intake_id INTO v_intake_id;

  -- 4. Bin & Subject Distribution Loop
  v_first_bin := NULL;
  FOR v_bin IN SELECT * FROM jsonb_array_elements(COALESCE(p_payload->'bins', '[]'::jsonb))
  LOOP
    v_bin_code := COALESCE(v_bin->>'bin_code', v_bin->>'bin_id');
    v_notes := COALESCE(v_bin->>'bin_notes', 'Clinical Intake Baseline');
    v_egg_count := COALESCE((v_bin->>'egg_count')::int, 0);
    
    IF v_bin_code IS NULL OR v_egg_count < 1 THEN
      RAISE EXCEPTION 'vault_finalize_intake: invalid bin entry';
    END IF;

    INSERT INTO public.bin (
      bin_code, intake_id, bin_notes, total_eggs,
      target_total_weight_g, substrate, shelf_location,
      session_id, created_by_id, modified_by_id
    ) VALUES (
      v_bin_code, v_intake_id, v_notes, v_egg_count,
      (v_bin->>'bin_weight_g')::numeric,
      v_bin->>'substrate', v_bin->>'shelf_location',
      v_session_id, v_observer_id, v_observer_id
    )
    RETURNING bin_id INTO v_generated_bin_id;

    IF v_first_bin IS NULL THEN
      v_first_bin := v_generated_bin_id;
    END IF;

    -- Baseline Bin Observation (Â§2)
    INSERT INTO public.bin_observation (
      session_id, bin_id, observer_id, observer_name,
      bin_weight_g, incubator_temp_f, env_notes,
      created_by_id, modified_by_id
    ) VALUES (
      v_session_id, v_generated_bin_id, v_observer_id, COALESCE(v_observer_name, 'QA_NODE'),
      (v_bin->>'bin_weight_g')::numeric,
      (v_bin->>'incubator_temp_f')::numeric,
      'Initial Clinical Intake Baseline',
      v_observer_id, v_observer_id
    );

    -- Biological Grid Initialization
    SELECT count(*)::int INTO v_eggs_in_bin FROM public.egg WHERE bin_id = v_generated_bin_id;
    FOR v_i IN 1..v_egg_count LOOP
      v_egg_code := v_bin_code || '-E' || (v_eggs_in_bin + v_i);
      
      INSERT INTO public.egg (
        egg_code, bin_id, status, current_stage, intake_date,
        session_id, created_by_id, modified_by_id
      ) VALUES (
        v_egg_code, v_generated_bin_id, 'Active', 'S1', v_intake_date,
        v_session_id, v_observer_id, v_observer_id
      ) RETURNING egg_id INTO v_numeric_egg_id;

      INSERT INTO public.egg_observation (
        session_id, egg_id, bin_id, observer_id,
        created_by_id, modified_by_id,
        stage_at_observation, observation_notes, is_deleted
      ) VALUES (
        v_session_id, v_numeric_egg_id, v_generated_bin_id, v_observer_id,
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
$function$

;

-- Function: public.vault_restore_from_backup
CREATE OR REPLACE FUNCTION public.vault_restore_from_backup(p_payload jsonb, p_session_id text, p_observer_id uuid)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
BEGIN
    -- Log intent
    INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
    VALUES (p_session_id, 'CRITICAL', 'Disaster Recovery JSON Restore Initiated', '{}'::jsonb, now());

    -- Truncate existing transactional data
    TRUNCATE TABLE public.intake, public.bin, public.egg, public.bin_observation, public.egg_observation, public.hatchling_ledger CASCADE;

    -- Bulk Restore using Postgres JSONB parsing
    IF p_payload->'intake' IS NOT NULL THEN
        INSERT INTO public.intake SELECT * FROM jsonb_populate_recordset(null::public.intake, p_payload->'intake');
    END IF;

    IF p_payload->'bin' IS NOT NULL THEN
        INSERT INTO public.bin SELECT * FROM jsonb_populate_recordset(null::public.bin, p_payload->'bin');
    END IF;

    IF p_payload->'egg' IS NOT NULL THEN
        INSERT INTO public.egg SELECT * FROM jsonb_populate_recordset(null::public.egg, p_payload->'egg');
    END IF;

    IF p_payload->'bin_observation' IS NOT NULL THEN
        INSERT INTO public.bin_observation SELECT * FROM jsonb_populate_recordset(null::public.bin_observation, p_payload->'bin_observation');
    END IF;

    IF p_payload->'egg_observation' IS NOT NULL THEN
        INSERT INTO public.egg_observation SELECT * FROM jsonb_populate_recordset(null::public.egg_observation, p_payload->'egg_observation');
    END IF;

    IF p_payload->'hatchling_ledger' IS NOT NULL THEN
        INSERT INTO public.hatchling_ledger SELECT * FROM jsonb_populate_recordset(null::public.hatchling_ledger, p_payload->'hatchling_ledger');
    END IF;

    IF p_payload->'system_log' IS NOT NULL THEN
        INSERT INTO public.system_log SELECT * FROM jsonb_populate_recordset(null::public.system_log, p_payload->'system_log') ON CONFLICT DO NOTHING;
    END IF;

    -- Log completion
    INSERT INTO public.system_log (session_id, event_type, event_message, payload, timestamp)
    VALUES (p_session_id, 'CRITICAL', 'Disaster Recovery JSON Restore Completed', '{}'::jsonb, now());
END;
$function$

;

-- Function: public.vault_supplemental_intake
CREATE OR REPLACE FUNCTION public.vault_supplemental_intake(p_payload jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$ 
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
$function$

;

-- Function: public.sync_modified_at
CREATE OR REPLACE FUNCTION public.sync_modified_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$function$

;

-- Function: public.vault_admin_restore
CREATE OR REPLACE FUNCTION public.vault_admin_restore(p_state_id integer, p_session_id text, p_observer_id uuid)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$
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
$function$

;

-- Function: public.generate_bin_id
CREATE OR REPLACE FUNCTION public.generate_bin_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
 DECLARE
     next_bin_num INTEGER;
 BEGIN
     IF NEW.bin_id IS NULL THEN
         SELECT COALESCE(COUNT(*), 0) + 1 INTO next_bin_num 
         FROM public.bin 
         WHERE intake_id = NEW.intake_id;
         
         NEW.bin_id := NEW.intake_id || '_B' || next_bin_num;
     END IF;
     RETURN NEW;
 END;
 $function$

;

-- Function: public.generate_obs_id
CREATE OR REPLACE FUNCTION public.generate_obs_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF NEW.obs_id IS NULL THEN
        NEW.obs_id := NEW.session_id || '_ENV_' || TO_CHAR(NEW.timestamp, 'HH24MISS');
    END IF;
    RETURN NEW;
END;
$function$

;

-- Function: public.generate_mother_id
CREATE OR REPLACE FUNCTION public.generate_mother_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF NEW.mother_id IS NULL THEN
        NEW.mother_id := REPLACE(NEW.mother_name, ' ', '') || '_' || 
                         NEW.species_id || '_' || 
                         TO_CHAR(NEW.intake_date, 'YYYYMMDD');
    END IF;
    RETURN NEW;
END;
$function$

;

-- Function: public.generate_egg_id
CREATE OR REPLACE FUNCTION public.generate_egg_id()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    next_egg_num INTEGER;
BEGIN
    IF NEW.egg_id IS NULL THEN
        SELECT COALESCE(COUNT(*), 0) + 1 INTO next_egg_num 
        FROM public.egg 
        WHERE bin_id = NEW.bin_id;
        
        NEW.egg_id := NEW.bin_id || '_E' || next_egg_num;
    END IF;
    RETURN NEW;
END;
$function$

;
