-- ============================================================================
-- CR-20260501-1800 v9.1.1: Fix vault RPCs for numeric bin_id auto-generation
-- bin.bin_id is now BIGINT GENERATED ALWAYS AS IDENTITY
-- RPCs must INSERT bin_code (text) and let DB auto-generate bin_id
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. Fix vault_finalize_intake: use bin_code, auto-generate bin_id
-- ============================================================================
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
    -- CR-20260501-1800: Read bin_code (text) from payload, not bin_id
    v_bin_code := COALESCE(v_bin->>'bin_code', v_bin->>'bin_id');
    v_notes := COALESCE(v_bin->>'bin_notes', 'Clinical Intake Baseline');
    v_egg_count := COALESCE((v_bin->>'egg_count')::int, 0);
    
    IF v_bin_code IS NULL OR v_egg_count < 1 THEN
      RAISE EXCEPTION 'vault_finalize_intake: invalid bin entry (must have bin_code and 1+ eggs)';
    END IF;

    -- CR-20260501-1800: INSERT bin_code, let BIGINT IDENTITY auto-generate bin_id
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

    -- Create Baseline Bin Observation
    INSERT INTO public.bin_observation (
      bin_observation_id, session_id, bin_id, observer_id,
      bin_weight_g, incubator_temp_f, env_notes,
      created_by_id, modified_by_id
    ) VALUES (
      'BO-' || v_generated_bin_id || '-' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS'),
      v_session_id, v_generated_bin_id, v_observer_id,
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

  -- CR-20260501-1800: Return numeric bin_id (BIGINT)
  RETURN jsonb_build_object(
    'intake_id', v_intake_id,
    'first_bin_id', v_first_bin
  );
END;
$function$;

GRANT EXECUTE ON FUNCTION public.vault_finalize_intake(jsonb) TO service_role;

-- ============================================================================
-- 2. Fix vault_finalize_supplemental_bin: use bin_code, auto-generate bin_id
-- ============================================================================
CREATE OR REPLACE FUNCTION vault_finalize_supplemental_bin(
    p_intake_id text,
    p_session_id text,
    p_observer_id uuid,
    p_observer_name text,
    p_supp_date date,
    p_bins jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_bin jsonb;
    v_bin_code text;
    v_generated_bin_id bigint;
    v_bin_count int := 0;
    v_new_egg_count int;
    v_current_egg_count int;
    v_total_eggs int;
    v_substrate text;
    v_shelf_location text;
    v_notes text;
    v_is_new_bin boolean;
    v_existing_bin_id bigint;
    v_bin_num int;
    v_next_egg_num int;
    v_egg_id text;
    v_egg_ids text[] := '{}';
    v_species_id text;
    v_species_code text;
    v_finder_clean text;
    v_intake_number int;
    v_obs_id text;
    v_result jsonb;
BEGIN
    SELECT i.species_id, s.species_code, i.finder_turtle_name, 
           COALESCE(i.intake_number, 0)
    INTO v_species_id, v_species_code, v_finder_clean, v_intake_number
    FROM public.intake i
    JOIN public.species s ON i.species_id = s.species_id
    WHERE i.intake_id = p_intake_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Intake % not found', p_intake_id;
    END IF;

    v_finder_clean := regexp_replace(upper(COALESCE(v_finder_clean, '')), '[^A-Z0-9]', '', 'g');
    IF v_finder_clean = '' THEN
        v_finder_clean := 'UNKNOWN';
    END IF;

    IF v_species_code IS NULL THEN
        v_species_code := v_species_id;
    END IF;

    IF v_intake_number IS NULL OR v_intake_number = 0 THEN
        SELECT COALESCE(MAX(intake_number), 0) + 1
        INTO v_intake_number
        FROM public.intake
        WHERE species_id = v_species_id;
        
        UPDATE public.intake 
        SET intake_number = v_intake_number
        WHERE intake_id = p_intake_id;
    END IF;

    FOR v_bin IN SELECT * FROM jsonb_array_elements(p_bins)
    LOOP
        v_new_egg_count := (v_bin->>'new_egg_count')::int;
        v_current_egg_count := COALESCE((v_bin->>'current_egg_count')::int, 0);
        v_total_eggs := (v_bin->>'total_eggs')::int;
        v_substrate := v_bin->>'substrate';
        v_shelf_location := v_bin->>'shelf';
        v_notes := v_bin->>'notes';
        v_is_new_bin := (v_bin->>'is_new_bin')::boolean;

        IF v_total_eggs IS NULL THEN
            v_total_eggs := v_current_egg_count + v_new_egg_count;
        END IF;

        IF v_total_eggs < 1 THEN
            RAISE EXCEPTION 'Bin must have at least 1 egg total';
        END IF;

        IF v_is_new_bin THEN
            -- CR-20260501-1800: Read bin_code from payload, generate unique code
            v_bin_code := v_bin->>'bin_code';
            IF v_bin_code IS NULL THEN
                -- Fallback: generate bin_code if not provided
                SELECT COALESCE(MAX(CAST(regexp_replace(bin_code, '.*-(\d+)$', '\1') AS INTEGER)), 0) + 1
                INTO v_bin_num
                FROM public.bin
                WHERE intake_id = p_intake_id;
                v_bin_code := v_species_code || LPAD(v_intake_number::text, 2, '0') || '-' || v_finder_clean || '-' || v_bin_num;
            END IF;

            -- CR-20260501-1800: INSERT bin_code, let BIGINT IDENTITY auto-generate bin_id
            INSERT INTO public.bin (
                bin_code, intake_id, total_eggs, bin_notes, substrate, shelf_location,
                session_id, created_by_id, modified_by_id
            )
            VALUES (
                v_bin_code, p_intake_id, v_total_eggs, v_notes, v_substrate, v_shelf_location,
                p_session_id, p_observer_id, p_observer_id
            )
            RETURNING bin_id INTO v_generated_bin_id;

            -- Insert eggs with baseline observations
            v_next_egg_num := 0;
            FOR i IN 1..v_total_eggs LOOP
                v_egg_id := v_bin_code || '-E' || i;
                INSERT INTO public.egg (
                    egg_id, bin_id, intake_date, status, current_stage,
                    session_id, created_by_id, modified_by_id
                ) VALUES (
                    v_egg_id, v_generated_bin_id, p_supp_date, 'Active', 'S1',
                    p_session_id, p_observer_id, p_observer_id
                );
                INSERT INTO public.egg_observation (
                    session_id, egg_id, bin_id, observer_id,
                    created_by_id, modified_by_id,
                    stage_at_observation, observation_notes, is_deleted
                ) VALUES (
                    p_session_id, v_egg_id, v_generated_bin_id, p_observer_id,
                    p_observer_id, p_observer_id,
                    'S1', 'Supplemental Intake Baseline', FALSE
                );
            END LOOP;
            v_bin_count := v_bin_count + 1;
        ELSE
            -- Existing bin: update total_eggs, run through RETURNING for bin_id
            v_existing_bin_id := (v_bin->>'existing_bin_id')::bigint;
            UPDATE public.bin
            SET total_eggs = v_total_eggs,
                bin_notes = v_notes,
                substrate = v_substrate,
                shelf_location = v_shelf_location,
                modified_by_id = p_observer_id,
                modified_at = NOW()
            WHERE bin_id = v_existing_bin_id
            RETURNING bin_id INTO v_generated_bin_id;

            -- Add new eggs if count increased
            IF v_new_egg_count > 0 THEN
                -- Get current egg count
                SELECT COALESCE(COUNT(*), 0) INTO v_next_egg_num
                FROM public.egg
                WHERE bin_id = v_existing_bin_id AND is_deleted = FALSE;

                -- Get bin_code for egg_id construction
                SELECT bin_code INTO v_bin_code
                FROM public.bin
                WHERE bin_id = v_existing_bin_id;

                FOR i IN 1..v_new_egg_count LOOP
                    v_egg_id := v_bin_code || '-E' || (v_next_egg_num + i);
                    INSERT INTO public.egg (
                        egg_id, bin_id, intake_date, status, current_stage,
                        session_id, created_by_id, modified_by_id
                    ) VALUES (
                        v_egg_id, v_existing_bin_id, p_supp_date, 'Active', 'S1',
                        p_session_id, p_observer_id, p_observer_id
                    );
                    INSERT INTO public.egg_observation (
                        session_id, egg_id, bin_id, observer_id,
                        created_by_id, modified_by_id,
                        stage_at_observation, observation_notes, is_deleted
                    ) VALUES (
                        p_session_id, v_egg_id, v_existing_bin_id, p_observer_id,
                        p_observer_id, p_observer_id,
                        'S1', 'Supplemental Intake Baseline', FALSE
                    );
                END LOOP;
            END IF;
        END IF;
    END LOOP;

    RETURN jsonb_build_object(
        'success', true,
        'bins_updated', v_bin_count,
        'intake_id', p_intake_id
    );
END;
$$;

GRANT EXECUTE ON FUNCTION vault_finalize_supplemental_bin(text, text, uuid, text, date, jsonb) TO service_role;

COMMIT;
