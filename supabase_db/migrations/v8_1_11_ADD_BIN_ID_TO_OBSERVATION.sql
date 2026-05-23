-- =============================================================================
-- SQL:        v8_1_11_ADD_BIN_ID_TO_OBSERVATION.sql
-- Project:    Incubator Vault v8.1.11
-- Purpose:    Adds missing 'bin_id' to 'egg_observation' to support clinical RPCs.
-- =============================================================================

BEGIN;

-- 1. Add bin_id column to egg_observation
ALTER TABLE public.egg_observation 
ADD COLUMN IF NOT EXISTS bin_id TEXT REFERENCES public.bin(bin_id);

-- 2. Clean up any existing orphaned records if necessary (none expected in clean test)

COMMIT;

-- Success row
SELECT 'Success' AS status, 'Column bin_id added to egg_observation.' AS message;
