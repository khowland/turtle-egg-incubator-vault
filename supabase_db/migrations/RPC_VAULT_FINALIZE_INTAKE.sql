-- =============================================================================
-- SQL:        RPC_VAULT_FINALIZE_INTAKE.sql
-- Project:    Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
-- Description: Single-transaction intake (ISS-5). Deploy after v8_1_0 migration.
-- Invoke from Python: supabase.rpc('vault_finalize_intake', {'p_payload': {...}})
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
    NULLIF(p_payload#>>'{intake,intake_name}', ''), -- Map payload keys too
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

    -- Standard v8.1.16: Capture mandatory bin metrics
    INSERT INTO public.bin (
      bin_id, 
      intake_id, 
      bin_notes, 
      total_eggs,
      target_total_weight_g,
      incubator_temp_c,
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
      (v_bin->>'incubator_temp_c')::numeric,
      v_bin->>'substrate',
      v_bin->>'shelf_location',
      v_session_id, 
      v_observer_id, 
      v_observer_id
    );

    -- Create Baseline Bin Observation (§2 Compliance)
    INSERT INTO public.bin_observation (
      bin_observation_id,
      session_id,
      bin_id,
      observer_id,
      bin_weight_g,
      incubator_temp_c,
      env_notes,
      created_by_id,
      modified_by_id
    ) VALUES (
      'BO-' || v_bin_id || '-' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS'),
      v_session_id,
      v_bin_id,
      v_observer_id,
      (v_bin->>'bin_weight_g')::numeric,
      (v_bin->>'incubator_temp_c')::numeric,
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
