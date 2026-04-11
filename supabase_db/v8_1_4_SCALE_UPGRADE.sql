-- =============================================================================
-- SQL:        v8_1_4_SCALE_UPGRADE.sql
-- Project:    WINC Incubator System
-- Description: Converts health flags from Boolean to Integer (0-3 Scale)
-- =============================================================================

BEGIN;

-- 1. Upgrade Observation Table: Convert booleans to integers
-- We use 1 for TRUE and 0 for FALSE during the migration.
ALTER TABLE public.egg_observation 
  ALTER COLUMN molding TYPE INTEGER USING (CASE WHEN molding THEN 1 ELSE 0 END),
  ALTER COLUMN leaking TYPE INTEGER USING (CASE WHEN leaking THEN 1 ELSE 0 END),
  ALTER COLUMN dented TYPE INTEGER USING (CASE WHEN dented THEN 1 ELSE 0 END);

-- 2. Add Persistently Tracked States to Core Egg Table for Analytics
-- This allows the UI grid to display latest health status without heavy scanning.
ALTER TABLE public.egg 
  ADD COLUMN IF NOT EXISTS last_molding INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS last_leaking INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS last_dented INTEGER DEFAULT 0;

-- 3. Set Defaults and Constrain Scales
ALTER TABLE public.egg_observation ALTER COLUMN molding SET DEFAULT 0;
ALTER TABLE public.egg_observation ALTER COLUMN leaking SET DEFAULT 0;
ALTER TABLE public.egg_observation ALTER COLUMN dented SET DEFAULT 0;

-- 4. Update existing records in egg table (best effort sync)
UPDATE public.egg e
SET 
  last_molding = (SELECT molding FROM public.egg_observation WHERE egg_id = e.egg_id ORDER BY timestamp DESC LIMIT 1),
  last_leaking = (SELECT leaking FROM public.egg_observation WHERE egg_id = e.egg_id ORDER BY timestamp DESC LIMIT 1),
  last_dented =  (SELECT dented FROM public.egg_observation WHERE egg_id = e.egg_id ORDER BY timestamp DESC LIMIT 1);

COMMIT;
