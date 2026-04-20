-- =============================================================================
-- SQL:        v8_1_20_RPC_VAULT_RESTORE_FROM_BACKUP.sql
-- Project:    Incubator Vault v8.1.4 
-- Description: Secure RPC to ingest a JSON backup payload and restore historical data
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_restore_from_backup(p_payload jsonb, p_session_id TEXT, p_observer_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
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
$$;

GRANT EXECUTE ON FUNCTION public.vault_restore_from_backup(jsonb, TEXT, UUID) TO service_role;
