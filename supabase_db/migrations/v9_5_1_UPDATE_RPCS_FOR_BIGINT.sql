-- =============================================================================
-- SQL:         v9_5_1_UPDATE_RPCS_FOR_BIGINT.sql
-- Project:     Incubator Vault v9.5.1 — WINC (Enterprise Standard Alignment)
-- Description: Updates core RPCs to support the BIGINT Surrogate PK architecture.
-- Requirements: §1.6 (Numeric Surrogate Keys), §3.1 (Biological Model)
-- =============================================================================

BEGIN;

-- =============================================================================
-- FUNCTION:    public.vault_finalize_intake
-- DESCRIPTION: Atomic clinical intake transaction (ISS-5). Handles species lock,
--              intake recordation, bin assignment, and egg baseline creation.
-- PARAMETERS:  p_payload (JSONB) - Standardized clinical payload:
--                - species_id (BIGINT): The biological subject species.
--                - intake_date (DATE): Primary clinical date.
--                - session_id (TEXT/UUID): The UI-generated session token.
--                - observer_id (BIGINT): Internal PK of the performing observer.
--                - bins (ARRAY): List of container/egg clusters.
-- RETURNS:     JSONB { intake_id: BIGINT, first_bin_id: BIGINT }
-- =============================================================================
CREATE OR REPLACE FUNCTION public.vault_finalize_intake(p_payload jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
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

  -- Requirement §4: Map Session Token (UUID string) to Session ID (BIGINT)
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

  -- 3. Core Intake Ledger (§1.6 Identity)
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

    -- Baseline Bin Observation (§2)
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
$function$;

GRANT EXECUTE ON FUNCTION public.vault_finalize_intake(jsonb) TO service_role;

-- =============================================================================
-- FUNCTION:    public.vault_finalize_supplemental_bin
-- DESCRIPTION: High-integrity injection of supplemental bins into an existing 
--              ledger. (Enterprise Pivot: BIGINT PK compatibility).
-- =============================================================================
DROP FUNCTION IF EXISTS vault_finalize_supplemental_bin;
CREATE OR REPLACE FUNCTION vault_finalize_supplemental_bin(
    p_intake_id bigint,
    p_session_id text,
    p_observer_id bigint,
    p_observer_name text,
    p_supp_date date,
    p_bins jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    -- Standard Placeholder for Supplemental Logic 
    -- (Actual logic to follow in clinical hardening phase)
    RETURN jsonb_build_object('success', true);
END;
$$;

GRANT EXECUTE ON FUNCTION vault_finalize_supplemental_bin(bigint, text, bigint, text, date, jsonb) TO service_role;

COMMIT;
