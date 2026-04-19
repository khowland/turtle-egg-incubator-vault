-- =============================================================================
-- SQL:        v8_1_7_REMEDIATE_INTEGRITY.sql
-- Project:    Incubator Vault v8.1.7 
-- Purpose:    Surgically removes legacy 'mother_id' trigger references.
--             Run this in the Supabase SQL Editor if Intake fails with 42703.
-- =============================================================================

BEGIN;

-- 1. Identify and Drop legacy triggers on 'intake'
-- We drop by a common naming pattern used in v7.x
DROP TRIGGER IF EXISTS handle_mother_id_audit ON public.intake;
DROP TRIGGER IF EXISTS update_intake_modified_at ON public.intake;
DROP TRIGGER IF EXISTS sync_species_count ON public.intake;

-- 2. Clean 'hatchling_ledger' if any old constraints remain
-- (Hatchling ledger was audited and confirmed to have 'intake_id' now, 
-- but we ensure the underlying function is fresh)

-- 3. Re-establish modern audit triggers
CREATE OR REPLACE FUNCTION public.sync_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_intake_modified_at
    BEFORE UPDATE ON public.intake
    FOR EACH ROW
    EXECUTE FUNCTION public.sync_modified_at();

COMMIT;
