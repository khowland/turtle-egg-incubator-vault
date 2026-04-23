-- =============================================================================
-- SQL:        v8_1_14_FINAL_NOMENCLATURE_FIX.sql
-- Project:    Incubator Vault v8.1.14
-- Purpose:    Final column renames for RPC compatibility.
-- =============================================================================

BEGIN;

-- 1. Align egg_observation: notes -> observation_notes
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'notes') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'observation_notes') THEN
        ALTER TABLE public.egg_observation RENAME COLUMN notes TO observation_notes;
    END IF;
END $$;

-- 2. Align bin_observation: notes -> observation_notes
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bin_observation' AND column_name = 'notes') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bin_observation' AND column_name = 'observation_notes') THEN
        ALTER TABLE public.bin_observation RENAME COLUMN notes TO observation_notes;
    END IF;
END $$;

-- 3. Ensure sub_stage_code exist in bin_observation (already in egg_observation from v8.1.13)
ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS sub_stage_code TEXT;

COMMIT;

-- Success row
SELECT 'Success' AS status, 'Observation notes nomenclature synchronized system-wide.' AS message;
