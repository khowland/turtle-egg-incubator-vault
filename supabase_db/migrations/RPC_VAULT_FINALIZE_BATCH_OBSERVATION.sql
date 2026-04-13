
CREATE OR REPLACE FUNCTION public.vault_finalize_batch_observation(p_payload jsonb)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_obs jsonb;
    v_egg_id text;
    v_session_id text;
    v_observer_id uuid;
    v_bin_id text;
    v_stage text;
    v_hatch_date date;
    v_intake_id text;
    v_incub_days int;
    v_intake_ts timestamptz;
    v_vitality text;
    v_obs_date date;
BEGIN
    v_session_id := p_payload->>'session_id';
    v_observer_id := (p_payload->>'observer_id')::uuid;
    v_stage := p_payload->>'stage';
    v_vitality := COALESCE(p_payload->>'vitality', 'pending_field_assessment');
    v_obs_date := COALESCE((p_payload->>'egg_observation_date')::date, CURRENT_DATE);

    FOR v_obs IN SELECT * FROM jsonb_array_elements(p_payload->'observations')
    LOOP
        v_egg_id := v_obs->>'egg_id';
        v_bin_id := v_obs->>'bin_id';

        INSERT INTO public.egg_observation (
            session_id, egg_id, bin_id, observer_id,
            created_by_id, modified_by_id,
            stage_at_observation, sub_stage_code, observation_notes, is_deleted,
            egg_observation_date,
            chalking, vascularity, molding, leaking, dented
        ) VALUES (
            v_session_id, v_egg_id, v_bin_id, v_observer_id,
            v_observer_id, v_observer_id,
            v_stage, p_payload->>'sub_stage', p_payload->>'observation_notes', FALSE,
            COALESCE((p_payload->>'egg_observation_date')::date, CURRENT_DATE),
            (v_obs->>'chalking')::int, (v_obs->>'vascularity')::boolean,
            (v_obs->>'molding')::int, (v_obs->>'leaking')::int, (v_obs->>'dented')::int
        );

        UPDATE public.egg
        SET current_stage = v_stage,
            status = CASE WHEN v_stage LIKE 'S6%' THEN 'Transferred' ELSE 'Active' END,
            last_chalk = (v_obs->>'chalking')::int,
            last_vasc = (v_obs->>'vascularity')::boolean,
            last_molding = (v_obs->>'molding')::int,
            last_leaking = (v_obs->>'leaking')::int,
            last_dented = (v_obs->>'dented')::int,
            egg_notes = COALESCE(p_payload->>'egg_notes', egg_notes),
            modified_by_id = v_observer_id,
            modified_at = now()
        WHERE egg_id = v_egg_id;

        IF v_stage LIKE 'S6%' THEN
            SELECT intake_timestamp INTO v_intake_ts FROM public.egg WHERE egg_id = v_egg_id;
            SELECT intake_id INTO v_intake_id FROM public.bin WHERE bin_id = v_bin_id;
            v_hatch_date := current_date;
            IF v_intake_ts IS NOT NULL THEN
                v_incub_days := v_hatch_date - v_intake_ts::date;
            END IF;

            INSERT INTO public.hatchling_ledger (
                egg_id, intake_id, hatch_date, vitality_score,
                incubation_duration_days, notes, session_id,
                created_by_id, modified_by_id
            ) VALUES (
                v_egg_id, v_intake_id, v_hatch_date, substring(v_vitality from 1 for 500),
                v_incub_days, 'Auto-recorded on S6 batch transition', v_session_id,
                v_observer_id, v_observer_id
            ) ON CONFLICT (egg_id) DO UPDATE SET
                hatch_date = EXCLUDED.hatch_date,
                vitality_score = EXCLUDED.vitality_score,
                incubation_duration_days = EXCLUDED.incubation_duration_days,
                modified_by_id = EXCLUDED.modified_by_id,
                modified_at = now();
        END IF;
    END LOOP;
END;
$$;
GRANT EXECUTE ON FUNCTION public.vault_finalize_batch_observation(jsonb) TO anon;
GRANT EXECUTE ON FUNCTION public.vault_finalize_batch_observation(jsonb) TO authenticated;
