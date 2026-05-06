-- ============================================================================
-- v9.2.1: Fix vault_finalize_intake — add observer_name to bin_observation INSERT
-- Root Cause: RPC inserts bin_observation without NOT NULL observer_name column
-- Fix: Extract observer_name from observer table (display_name) and include it
-- ============================================================================

BEGIN;

-- Updated vault_finalize_intake with observer_name extraction
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
  v_observer_name text;
  v_intake_id text;
  v_bin jsonb;
  v_bin_code text;
  v_generated_bin_id bigint;
  v_notes text;
  v_egg_count int;
  v_i int;
  v_egg_id text;
  v_eggs_in_bin int;
  v_first_bin bigint;
BEGIN
  v_species_id := p_payload->>'species_id';
  v_intake_date := (p_payload->>'intake_date')::date;
  v_session_id := p_payload->>'session_id';
  v_observer_id := (p_payload->>'observer_id')::uuid;

  -- CR-20260506-0547 v9.2.1: Extract observer_name from observer table
  SELECT display_name INTO v_observer_name
  FROM public.observer
  WHERE observer_id = v_observer_id;

  IF v_observer_name IS NULL THEN
    RAISE EXCEPTION 'vault_finalize_intake: observer_id % not found in observer table', v_observer_id;
  END IF;

  IF v_species_id IS NULL OR v_session_id IS NULL OR v_observer_id IS NULL THEN
    RAISE EXCEPTION 'vault_finalize_intake: missing required payload fields';
  END IF;

  SELECT intake_count INTO v_next_intake FROM public.species WHERE species_id = v_species_id FOR UPDATE;
  IF NOT FOUND THEN
    RAISE EXCEPTION 'vault_finalize_intake: species_id % not found', v_species_id;
  END IF;
  
  v_next_intake := v_next_intake + 1;
  UPDATE public.species SET intake_count = v_next_intake WHERE species_id = v_species_id;

  v_intake_id := 'I' || to_char(clock_timestamp(), 'YYYYMMDDHH24MS');

  INSERT INTO public.intake (
    intake_id, intake_name, finder_turtle_name, species_id, intake_date,
    intake_condition, extraction_method, discovery_location,
    mother_weight_g, days_in_care, clinical_metadata,
    session_id, created_by_id, modified_by_id
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
    v_session_id, v_observer_id, v_observer_id
  );

  v_first_bin := NULL;
  FOR v_bin IN SELECT * FROM jsonb_array_elements(COALESCE(p_payload->'bins', '[]'::jsonb))
  LOOP
    v_bin_code := COALESCE(v_bin->>'bin_code', v_bin->>'bin_id');
    v_notes := COALESCE(v_bin->>'bin_notes', 'Clinical Intake Baseline');
    v_egg_count := COALESCE((v_bin->>'egg_count')::int, 0);
    
    IF v_bin_code IS NULL OR v_egg_count < 1 THEN
      RAISE EXCEPTION 'vault_finalize_intake: invalid bin entry (must have bin_code and 1+ eggs)';
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

    -- Create Baseline Bin Observation (NOW WITH observer_name)
    INSERT INTO public.bin_observation (
      bin_observation_id, session_id, bin_id, observer_id, observer_name,
      bin_weight_g, incubator_temp_f, env_notes,
      created_by_id, modified_by_id
    ) VALUES (
      'BO-' || v_generated_bin_id || '-' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS'),
      v_session_id, v_generated_bin_id, v_observer_id, v_observer_name,
      (v_bin->>'bin_weight_g')::numeric,
      (v_bin->>'incubator_temp_f')::numeric,
      'Initial Clinical Intake Baseline',
      v_observer_id, v_observer_id
    );

    SELECT count(*)::int INTO v_eggs_in_bin FROM public.egg WHERE bin_id = v_generated_bin_id;
    FOR v_i IN 1..v_egg_count LOOP
      v_egg_id := v_bin_code || '-E' || (v_eggs_in_bin + v_i);
      INSERT INTO public.egg (
        egg_id, bin_id, status, current_stage, intake_date,
        session_id, created_by_id, modified_by_id
      ) VALUES (
        v_egg_id, v_generated_bin_id, 'Active', 'S1', v_intake_date,
        v_session_id, v_observer_id, v_observer_id
      );
      INSERT INTO public.egg_observation (
        session_id, egg_id, bin_id, observer_id,
        created_by_id, modified_by_id,
        stage_at_observation, observation_notes, is_deleted
      ) VALUES (
        v_session_id, v_egg_id, v_generated_bin_id, v_observer_id,
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

GRANT EXECUTE ON FUNCTION public.vault_finalize_intake(jsonb) TO service_role;

COMMIT;
