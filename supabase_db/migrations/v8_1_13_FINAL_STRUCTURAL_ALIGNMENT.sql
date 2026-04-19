-- =============================================================================
-- SQL:        v8_1_13_FINAL_STRUCTURAL_ALIGNMENT.sql
-- Project:    Incubator Vault v8.1.13
-- Purpose:    Aligns egg_observation schema with RPC requirements.
-- =============================================================================

BEGIN;

-- 1. Rename 'timestamp' to 'egg_observation_date' if it exists and 'egg_observation_date' doesn't
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'timestamp') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'egg_observation_date') THEN
        ALTER TABLE public.egg_observation RENAME COLUMN "timestamp" TO egg_observation_date;
    END IF;
END $$;

-- 2. Add missing clinical metadata columns
ALTER TABLE public.egg_observation 
    ADD COLUMN IF NOT EXISTS sub_stage_code TEXT,
    ADD COLUMN IF NOT EXISTS observer_id UUID REFERENCES public.observer(observer_id);

-- 3. Ensure 'chalking' is integer (Scale 0-2)
-- (Already integer in export, but we keep it here for parity)

-- 4. Backfill observer_id from created_by_id
UPDATE public.egg_observation 
SET observer_id = created_by_id 
WHERE observer_id IS NULL AND created_by_id IS NOT NULL;

COMMIT;

-- Success row
SELECT 'Success' AS status, 'Structural alignment for egg_observation completed.' AS message;
