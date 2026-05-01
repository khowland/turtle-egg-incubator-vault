-- CR-20260429-225412: Atomic RPC for supplemental bin creation
-- Resolves red team blockers: observer_name NOT NULL, PENDING bin IDs, 
-- validation failures, intake_number race conditions, orphaned records
--
-- Corrected 2026-05-01: Verified against actual database schema via information_schema
-- - egg table: NO intake_id, NO species_id, NO observer_id columns
-- - egg_observation: NO observer_name column; has observer_id (uuid)
-- - bin_observation: NO substrate/shelf_location; has observer_name (text NOT NULL)
-- - session_log: session_id is text PK
-- - intake.intake_id is text (not uuid)
-- - species.species_code is character(1) type
CREATE OR REPLACE FUNCTION vault_finalize_supplemental_bin(
    p_intake_id text,
    p_session_id text,
    p_observer_id uuid,
    p_observer_name text,
    p_supp_date date,
    p_bins jsonb  -- array of bin objects
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_bin jsonb;
    v_bin_id text;
    v_bin_count int := 0;
    v_new_egg_count int;
    v_current_egg_count int;
    v_total_eggs int;
    v_substrate text;
    v_shelf_location text;
    v_notes text;
    v_is_new_bin boolean;
    v_existing_bin_id text;
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
    -- Get intake details for bin code generation
    SELECT i.species_id, s.species_code, i.finder_turtle_name, 
           COALESCE(i.intake_number, 0)
    INTO v_species_id, v_species_code, v_finder_clean, v_intake_number
    FROM public.intake i
    JOIN public.species s ON i.species_id = s.species_id
    WHERE i.intake_id = p_intake_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Intake % not found', p_intake_id;
    END IF;

    -- Generate clean finder code: uppercase, strip non-alphanumeric
    v_finder_clean := regexp_replace(upper(COALESCE(v_finder_clean, '')), '[^A-Z0-9]', '', 'g');
    IF v_finder_clean = '' THEN
        v_finder_clean := 'UNKNOWN';
    END IF;

    -- Get species_code for bin ID prefix (fallback to species_id if code is NULL)
    IF v_species_code IS NULL THEN
        v_species_code := v_species_id;
    END IF;

    -- Get next intake_number if not set (increment for this species)
    IF v_intake_number IS NULL OR v_intake_number = 0 THEN
        SELECT COALESCE(MAX(intake_number), 0) + 1
        INTO v_intake_number
        FROM public.intake
        WHERE species_id = v_species_id;
        
        UPDATE public.intake 
        SET intake_number = v_intake_number
        WHERE intake_id = p_intake_id;
    END IF;

    -- Process each bin in the array
    FOR v_bin IN SELECT * FROM jsonb_array_elements(p_bins)
    LOOP
        v_new_egg_count := (v_bin->>'new_egg_count')::int;
        v_current_egg_count := COALESCE((v_bin->>'current_egg_count')::int, 0);
        v_total_eggs := (v_bin->>'total_eggs')::int;
        v_substrate := v_bin->>'substrate';
        v_shelf_location := v_bin->>'shelf';
        v_notes := v_bin->>'notes';
        v_is_new_bin := (v_bin->>'is_new_bin')::boolean;
        v_existing_bin_id := v_bin->>'existing_bin_id';

        -- Derive total_eggs if not explicitly provided
        IF v_total_eggs IS NULL THEN
            v_total_eggs := v_current_egg_count + v_new_egg_count;
        END IF;

        -- Validate
        IF v_total_eggs < 1 THEN
            RAISE EXCEPTION 'Bin must have at least 1 egg total';
        END IF;

        IF v_is_new_bin THEN
            -- Get next bin number for this intake
            SELECT COALESCE(MAX(CAST(regexp_replace(bin_id, '.*-(\d+)$', '\1') AS INTEGER)), 0) + 1
            INTO v_bin_num
            FROM public.bin
            WHERE intake_id = p_intake_id;

            -- Generate bin_id: {species_code}{intake_number:02d}-{finder}-{bin_num}
            v_bin_id := v_species_code || LPAD(v_intake_number::text, 2, '0') || '-' || v_finder_clean || '-' || v_bin_num;

            -- Insert bin (matching actual bin table columns)
            INSERT INTO public.bin (
                bin_id, intake_id, total_eggs, bin_notes, substrate, shelf_location,
                session_id, created_by_id, modified_by_id, bin_code
            )
            VALUES (
                v_bin_id, p_intake_id, v_total_eggs, v_notes, v_substrate, v_shelf_location,
                p_session_id, p_observer_id, p_observer_id, v_bin_id
            );

            -- Insert eggs with baseline observations
            v_next_egg_num := 0;
            FOR i IN 1..v_total_eggs LOOP
                v_egg_id := v_bin_id || '-E' || i;
                INSERT INTO public.egg (
                    egg_id, bin_id, intake_date, status, current_stage,
                    session_id, created_by_id, modified_by_id
                )
                VALUES (
                    v_egg_id, v_bin_id, p_supp_date, 'Active', 'S1',
                    p_session_id, p_observer_id, p_observer_id
                );
                
                v_egg_ids := array_append(v_egg_ids, v_egg_id);

                -- Insert S1 baseline egg_observation (matches actual columns)
                INSERT INTO public.egg_observation (
                    egg_id, stage_at_observation, observation_notes,
                    session_id, observer_id, created_by_id, modified_by_id
                )
                VALUES (
                    v_egg_id, 'S1', 'Supplemental Intake Baseline',
                    p_session_id, p_observer_id, p_observer_id, p_observer_id
                );
            END LOOP;

            -- Insert initial bin_observation baseline (matching actual columns)
            v_obs_id := v_bin_id || '-OBS-' || EXTRACT(EPOCH FROM now())::bigint::text;
            INSERT INTO public.bin_observation (
                bin_observation_id, bin_id, session_id, observer_name, observation_notes,
                created_by_id, modified_by_id
            )
            VALUES (
                v_obs_id, v_bin_id, p_session_id, p_observer_name, 'Supplemental Intake Baseline',
                p_observer_id, p_observer_id
            );

            v_bin_count := v_bin_count + 1;
        ELSE
            -- Update existing bin: add new eggs to existing bin
            IF v_new_egg_count > 0 THEN
                -- Get existing egg count to determine next egg number
                SELECT COALESCE(MAX(CAST(SUBSTRING(egg_id FROM 'E(\d+)$') AS INTEGER)), 0)
                INTO v_next_egg_num
                FROM public.egg
                WHERE bin_id = v_existing_bin_id;

                -- Insert new eggs
                FOR i IN 1..v_new_egg_count LOOP
                    v_egg_id := v_existing_bin_id || '-E' || (v_next_egg_num + i);
                    INSERT INTO public.egg (
                        egg_id, bin_id, intake_date, status, current_stage,
                        session_id, created_by_id, modified_by_id
                    )
                    VALUES (
                        v_egg_id, v_existing_bin_id, p_supp_date, 'Active', 'S1',
                        p_session_id, p_observer_id, p_observer_id
                    );
                    
                    v_egg_ids := array_append(v_egg_ids, v_egg_id);

                    -- Insert S1 baseline egg_observation
                    INSERT INTO public.egg_observation (
                        egg_id, stage_at_observation, observation_notes,
                        session_id, observer_id, created_by_id, modified_by_id
                    )
                    VALUES (
                        v_egg_id, 'S1', 'Supplemental Intake Baseline',
                        p_session_id, p_observer_id, p_observer_id, p_observer_id
                    );
                END LOOP;

                -- Update total_eggs on existing bin
                UPDATE public.bin 
                SET total_eggs = total_eggs + v_new_egg_count,
                    modified_by_id = p_observer_id,
                    modified_at = now()
                WHERE bin_id = v_existing_bin_id;
            END IF;

            -- Insert bin_observation only if substrate or shelf changed
            IF v_substrate IS NOT NULL OR v_shelf_location IS NOT NULL THEN
                v_obs_id := v_existing_bin_id || '-OBS-' || EXTRACT(EPOCH FROM now())::bigint::text;
                INSERT INTO public.bin_observation (
                    bin_observation_id, bin_id, session_id, observer_name, observation_notes,
                    created_by_id, modified_by_id
                )
                VALUES (
                    v_obs_id, v_existing_bin_id, p_session_id, p_observer_name, 'Supplemental Configuration Update',
                    p_observer_id, p_observer_id
                );
            END IF;

            v_bin_id := v_existing_bin_id;
        END IF;
    END LOOP;

    -- Register session if needed
    INSERT INTO public.session_log (session_id, user_name)
    VALUES (p_session_id, p_observer_name)
    ON CONFLICT (session_id) DO NOTHING;

    -- Insert system_log audit entry
    INSERT INTO public.system_log (session_id, event_type, event_message, observer_id)
    VALUES (p_session_id, 'AUDIT', 
            'Supplemental intake: ' || v_bin_count || ' bins added to intake ' || p_intake_id,
            p_observer_id);

    -- Return result
    v_result := jsonb_build_object(
        'success', true,
        'intake_id', p_intake_id,
        'bins_processed', v_bin_count,
        'egg_ids', v_egg_ids
    );

    RETURN v_result;

EXCEPTION WHEN OTHERS THEN
    -- Log error and re-raise
    INSERT INTO public.system_log (session_id, event_type, event_message, observer_id)
    VALUES (p_session_id, 'ERROR', 
            'vault_finalize_supplemental_bin failed: ' || SQLERRM,
            p_observer_id);
    RAISE;
END;
$$;

-- Grant execution
GRANT EXECUTE ON FUNCTION vault_finalize_supplemental_bin(text, text, uuid, text, date, jsonb) TO authenticated, anon, service_role;
