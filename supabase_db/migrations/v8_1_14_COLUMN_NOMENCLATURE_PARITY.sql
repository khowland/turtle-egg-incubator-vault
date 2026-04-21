-- =============================================================================
-- SQL:        v8_1_14_COLUMN_NOMENCLATURE_PARITY.sql
-- Project:    Incubator Vault v8.1.14
-- Purpose:    Aligns column names between schema and RPC (notes -> observation_notes).
-- =============================================================================

BEGIN;

-- 1. Align egg_observation
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'notes') THEN
        ALTER TABLE public.egg_observation RENAME COLUMN notes TO observation_notes;
    END IF;
END $$;

-- 2. Align bin_observation
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bin_observation' AND column_name = 'notes') THEN
        ALTER TABLE public.bin_observation RENAME COLUMN notes TO observation_notes;
    END IF;
END $$;

COMMIT;

-- Success row
SELECT 'Success' AS status, 'Column notes renamed to observation_notes across clinical tables.' AS message;
