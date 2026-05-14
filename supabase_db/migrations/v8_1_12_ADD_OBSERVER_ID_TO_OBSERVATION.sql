-- =============================================================================
-- SQL:        v8_1_12_ADD_OBSERVER_ID_TO_OBSERVATION.sql
-- Project:    Incubator Vault v8.1.12
-- Purpose:    Adds missing 'observer_id' to 'egg_observation' to support clinical RPCs.
-- =============================================================================

BEGIN;

-- 1. Add observer_id column to egg_observation
ALTER TABLE public.egg_observation 
ADD COLUMN IF NOT EXISTS observer_id UUID REFERENCES public.observer(observer_id);

-- 2. Backfill existing records from created_by_id
UPDATE public.egg_observation 
SET observer_id = created_by_id 
WHERE observer_id IS NULL AND created_by_id IS NOT NULL;

COMMIT;

-- Success row
SELECT 'Success' AS status, 'Column observer_id added to egg_observation and backfilled.' AS message;
