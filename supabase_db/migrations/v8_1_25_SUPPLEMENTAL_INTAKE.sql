-- =============================================================================
-- SQL:        v8_1_25_SUPPLEMENTAL_INTAKE.sql
-- Project:    Incubator Vault v8.1.0 — WINC
-- Description: Atomic RPC for adding eggs/bins to an existing laying mother.
--              Handles DB locks, sequence incrementing, and S1 baselines.
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
      INSERT INTO public.bin (
        bin_id, intake_id, bin_notes, total_eggs, target_total_weight_g,
        incubator_temp_c, substrate, shelf_location, session_id, created_by_id, modified_by_id
      ) VALUES (
        v_bin_id, v_intake_id, COALESCE(v_bin->>'notes', 'Supplemental Bin'), v_new_egg_count,
        (v_bin->>'mass')::numeric, (v_bin->>'temp')::numeric, v_bin->>'substrate', v_bin->>'shelf',
        v_session_id, v_observer_id, v_observer_id
      );

      -- Baseline Bin Observation
      INSERT INTO public.bin_observation (
        bin_observation_id, session_id, bin_id, observer_id, bin_weight_g, incubator_temp_c, env_notes, created_by_id, modified_by_id
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
