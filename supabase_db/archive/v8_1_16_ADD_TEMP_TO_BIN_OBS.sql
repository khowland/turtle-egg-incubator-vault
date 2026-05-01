-- =============================================================================
-- SQL:        v8_1_16_ADD_TEMP_TO_BIN_OBS.sql
-- Project:    Incubator Vault v8.1.16
-- Purpose:    Add temperature tracking to bins and observations for clinical hardening.
-- =============================================================================

BEGIN;

-- 1. Add incubator_temp_c to public.bin (for current context/target)
ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS incubator_temp_c NUMERIC;

-- 2. Add incubator_temp_c to public.bin_observation (for historical tracking)
ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS incubator_temp_c NUMERIC;

COMMIT;

SELECT 'Success' AS status, 'Incubator temperature columns added to bin and bin_observation.' AS message;
