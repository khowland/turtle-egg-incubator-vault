-- =============================================================================
-- SQL:        v8_1_17_RPC_VAULT_EXPORT_BACKUP.sql
-- Project:    Incubator Vault v8.1.4 — Red Team DB State Architecture
-- Description: Secure RPC to export all transactional data for the Dead Man's Switch
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_export_full_backup()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_result jsonb;
BEGIN
    SELECT jsonb_build_object(
        'intake', (SELECT COALESCE(jsonb_agg(row_to_json(i)), '[]'::jsonb) FROM public.intake i),
        'bin', (SELECT COALESCE(jsonb_agg(row_to_json(b)), '[]'::jsonb) FROM public.bin b),
        'egg', (SELECT COALESCE(jsonb_agg(row_to_json(e)), '[]'::jsonb) FROM public.egg e),
        'bin_observation', (SELECT COALESCE(jsonb_agg(row_to_json(bo)), '[]'::jsonb) FROM public.bin_observation bo),
        'egg_observation', (SELECT COALESCE(jsonb_agg(row_to_json(eo)), '[]'::jsonb) FROM public.egg_observation eo),
        'hatchling_ledger', (SELECT COALESCE(jsonb_agg(row_to_json(hl)), '[]'::jsonb) FROM public.hatchling_ledger hl),
        'system_log', (SELECT COALESCE(jsonb_agg(row_to_json(sl)), '[]'::jsonb) FROM public.system_log sl),
        'timestamp', now()
    ) INTO v_result;
    
    RETURN v_result;
END;
$$;

GRANT EXECUTE ON FUNCTION public.vault_export_full_backup() TO service_role;
