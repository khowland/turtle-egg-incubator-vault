-- =============================================================================
-- SQL:        MIGRATE_ENTERPRISE_SCHEMA.sql
-- Project:    Incubator Vault v7.9.9 — "Titan Engine" 
-- Purpose:    Hardens legacy database to Enterprise Standards (§35).
--             Corrected for UUID type parity.
-- =============================================================================

BEGIN;

-- 1. Table Consistency (Snake_case, Singular)
ALTER TABLE IF EXISTS public.systemlog RENAME TO system_log;
ALTER TABLE IF EXISTS public.sessionlog RENAME TO session_log;
ALTER TABLE IF EXISTS public.eggobservation RENAME TO egg_observation;
ALTER TABLE IF EXISTS public.incubatorobservation RENAME TO bin_observation;

-- 2. Primary Key Refactor (Contextual Identifiers)
ALTER TABLE public.system_log RENAME COLUMN log_id TO system_log_id;
ALTER TABLE public.egg_observation RENAME COLUMN detail_id TO egg_observation_id;
ALTER TABLE public.bin_observation RENAME COLUMN obs_id TO bin_observation_id;
ALTER TABLE public.hatchling_ledger RENAME COLUMN id TO hatchling_ledger_id;

-- 3. Observer Table Cleanup
-- Note: id is UUID in the current production environment
ALTER TABLE public.observer RENAME COLUMN id TO observer_id;

-- 4. Clinical Column Expansion (Missing Metrics)
ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS bin_weight_g DECIMAL(10,2);
ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);
ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS env_notes TEXT;

ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS dented BOOLEAN DEFAULT FALSE;
ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS discolored BOOLEAN DEFAULT FALSE;
ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS moisture_deficit_g DECIMAL(10,2);
ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);
ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS stage_at_observation TEXT;

-- 5. Authorship Alignment (§35.4) - Fixed with UUID types
ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS modified_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS session_id TEXT REFERENCES public.session_log(session_id);

ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS modified_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.egg ADD COLUMN IF NOT EXISTS session_id TEXT REFERENCES public.session_log(session_id);

ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS modified_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.mother ADD COLUMN IF NOT EXISTS session_id TEXT REFERENCES public.session_log(session_id);

ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.egg_observation ADD COLUMN IF NOT EXISTS modified_by_id UUID REFERENCES public.observer(observer_id);

ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES public.observer(observer_id);
ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS modified_by_id UUID REFERENCES public.observer(observer_id);

COMMIT;
