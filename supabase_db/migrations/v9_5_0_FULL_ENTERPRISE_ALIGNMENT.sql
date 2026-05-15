-- v9_5_0_FULL_ENTERPRISE_ALIGNMENT.sql
-- Description: Enterprise Standard Alignment - BIGINT Surrogate Keys for ALL Tables
-- Strategy: "Wipe and Align" (Safe for Pre-Production / QA Environments)
-- Actions:
--   1. Truncate all data.
--   2. Drop all TEXT/UUID Primary Keys and cascade drop their foreign keys.
--   3. Create BIGINT GENERATED ALWAYS AS IDENTITY Primary Keys for all tables.
--   4. Recreate all Foreign Key columns as BIGINT.
--   5. Re-establish all Foreign Key constraints.

BEGIN;

-- ============================================================================
-- 1. WIPE ALL DATA (Clean Slate for Structural Overhaul)
-- ============================================================================
TRUNCATE TABLE public.hatchling_ledger CASCADE;
TRUNCATE TABLE public.egg_observation CASCADE;
TRUNCATE TABLE public.bin_observation CASCADE;
TRUNCATE TABLE public.egg CASCADE;
TRUNCATE TABLE public.bin CASCADE;
TRUNCATE TABLE public.intake CASCADE;
TRUNCATE TABLE public.session_log CASCADE;
TRUNCATE TABLE public.system_log CASCADE;
TRUNCATE TABLE public.biological_property CASCADE;
TRUNCATE TABLE public.development_stage CASCADE;
TRUNCATE TABLE public.species CASCADE;
TRUNCATE TABLE public.observer CASCADE;
TRUNCATE TABLE public.system_config CASCADE;

-- ============================================================================
-- 2. CONVERT PRIMARY KEYS TO BIGINT (and add CODE columns for UI display)
-- ============================================================================

-- SPECIES
ALTER TABLE public.species DROP CONSTRAINT IF EXISTS species_pkey CASCADE;
ALTER TABLE public.species DROP COLUMN IF EXISTS species_code;
ALTER TABLE public.species ADD COLUMN species_code TEXT; 
ALTER TABLE public.species ADD COLUMN species_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.species DROP COLUMN species_id CASCADE;
ALTER TABLE public.species RENAME COLUMN species_id_new TO species_id;
ALTER TABLE public.species ADD PRIMARY KEY (species_id);

-- OBSERVER
ALTER TABLE public.observer DROP CONSTRAINT IF EXISTS observer_pkey CASCADE;
ALTER TABLE public.observer ADD COLUMN observer_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.observer DROP COLUMN observer_id CASCADE;
ALTER TABLE public.observer RENAME COLUMN observer_id_new TO observer_id;
ALTER TABLE public.observer ADD PRIMARY KEY (observer_id);

-- SESSION_LOG
ALTER TABLE public.session_log DROP CONSTRAINT IF EXISTS session_log_pkey CASCADE;
ALTER TABLE public.session_log DROP COLUMN IF EXISTS session_token;
ALTER TABLE public.session_log ADD COLUMN session_token TEXT; -- Stores the UUID string from the UI
ALTER TABLE public.session_log ADD COLUMN session_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.session_log DROP COLUMN session_id CASCADE;
ALTER TABLE public.session_log RENAME COLUMN session_id_new TO session_id;
ALTER TABLE public.session_log ADD PRIMARY KEY (session_id);

-- INTAKE
ALTER TABLE public.intake DROP CONSTRAINT IF EXISTS intake_pkey CASCADE;
ALTER TABLE public.intake ADD COLUMN intake_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.intake DROP COLUMN intake_id CASCADE;
ALTER TABLE public.intake RENAME COLUMN intake_id_new TO intake_id;
ALTER TABLE public.intake ADD PRIMARY KEY (intake_id);

-- EGG
ALTER TABLE public.egg DROP CONSTRAINT IF EXISTS egg_pkey CASCADE;
ALTER TABLE public.egg DROP COLUMN IF EXISTS egg_code;
ALTER TABLE public.egg ADD COLUMN egg_code TEXT; -- Stores "2026-0001-E1"
ALTER TABLE public.egg ADD COLUMN egg_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.egg DROP COLUMN egg_id CASCADE;
ALTER TABLE public.egg RENAME COLUMN egg_id_new TO egg_id;
ALTER TABLE public.egg ADD PRIMARY KEY (egg_id);

-- BIN_OBSERVATION
ALTER TABLE public.bin_observation DROP CONSTRAINT IF EXISTS bin_observation_pkey CASCADE;
ALTER TABLE public.bin_observation ADD COLUMN bin_observation_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.bin_observation DROP COLUMN bin_observation_id CASCADE;
ALTER TABLE public.bin_observation RENAME COLUMN bin_observation_id_new TO bin_observation_id;
ALTER TABLE public.bin_observation ADD PRIMARY KEY (bin_observation_id);

-- HATCHLING_LEDGER
ALTER TABLE public.hatchling_ledger DROP CONSTRAINT IF EXISTS hatchling_ledger_pkey CASCADE;
ALTER TABLE public.hatchling_ledger ADD COLUMN hatchling_ledger_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.hatchling_ledger DROP COLUMN hatchling_ledger_id CASCADE;
ALTER TABLE public.hatchling_ledger RENAME COLUMN hatchling_ledger_id_new TO hatchling_ledger_id;
ALTER TABLE public.hatchling_ledger ADD PRIMARY KEY (hatchling_ledger_id);

-- SYSTEM_CONFIG
ALTER TABLE public.system_config DROP CONSTRAINT IF EXISTS system_config_pkey CASCADE;
ALTER TABLE public.system_config DROP COLUMN IF EXISTS config_name;
ALTER TABLE public.system_config ADD COLUMN config_name TEXT;
ALTER TABLE public.system_config ADD COLUMN config_key_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.system_config DROP COLUMN config_key CASCADE;
ALTER TABLE public.system_config RENAME COLUMN config_key_new TO config_key;
ALTER TABLE public.system_config ADD PRIMARY KEY (config_key);

-- BIOLOGICAL_PROPERTY
ALTER TABLE public.biological_property DROP CONSTRAINT IF EXISTS biological_property_pkey CASCADE;
ALTER TABLE public.biological_property ADD COLUMN property_id_new BIGINT GENERATED ALWAYS AS IDENTITY;
ALTER TABLE public.biological_property DROP COLUMN property_id CASCADE;
ALTER TABLE public.biological_property RENAME COLUMN property_id_new TO property_id;
ALTER TABLE public.biological_property ADD PRIMARY KEY (property_id);

-- Note: bin, egg_observation, system_log, and development_stage are already BIGINT PKs.

-- ============================================================================
-- 3. CONVERT FOREIGN KEY COLUMNS TO BIGINT
-- ============================================================================

-- INTAKE
ALTER TABLE public.intake 
  DROP COLUMN IF EXISTS species_id, DROP COLUMN IF EXISTS created_by_session, DROP COLUMN IF EXISTS updated_by_session, 
  DROP COLUMN IF EXISTS deleted_by_session, DROP COLUMN IF EXISTS created_by_id, DROP COLUMN IF EXISTS modified_by_id, DROP COLUMN IF EXISTS session_id;
ALTER TABLE public.intake 
  ADD COLUMN species_id BIGINT, ADD COLUMN created_by_session BIGINT, ADD COLUMN updated_by_session BIGINT, 
  ADD COLUMN deleted_by_session BIGINT, ADD COLUMN created_by_id BIGINT, ADD COLUMN modified_by_id BIGINT, ADD COLUMN session_id BIGINT;

-- BIN
ALTER TABLE public.bin 
  DROP COLUMN IF EXISTS intake_id, DROP COLUMN IF EXISTS created_by_session, DROP COLUMN IF EXISTS updated_by_session, 
  DROP COLUMN IF EXISTS deleted_by_session, DROP COLUMN IF EXISTS created_by_id, DROP COLUMN IF EXISTS modified_by_id, DROP COLUMN IF EXISTS session_id;
ALTER TABLE public.bin 
  ADD COLUMN intake_id BIGINT, ADD COLUMN created_by_session BIGINT, ADD COLUMN updated_by_session BIGINT, 
  ADD COLUMN deleted_by_session BIGINT, ADD COLUMN created_by_id BIGINT, ADD COLUMN modified_by_id BIGINT, ADD COLUMN session_id BIGINT;

-- EGG
ALTER TABLE public.egg 
  DROP COLUMN IF EXISTS created_by_session, DROP COLUMN IF EXISTS updated_by_session, DROP COLUMN IF EXISTS deleted_by_session, 
  DROP COLUMN IF EXISTS created_by_id, DROP COLUMN IF EXISTS modified_by_id, DROP COLUMN IF EXISTS session_id;
ALTER TABLE public.egg 
  ADD COLUMN created_by_session BIGINT, ADD COLUMN updated_by_session BIGINT, ADD COLUMN deleted_by_session BIGINT, 
  ADD COLUMN created_by_id BIGINT, ADD COLUMN modified_by_id BIGINT, ADD COLUMN session_id BIGINT;

-- BIN_OBSERVATION
ALTER TABLE public.bin_observation 
  DROP COLUMN IF EXISTS session_id, DROP COLUMN IF EXISTS deleted_by_session, DROP COLUMN IF EXISTS created_by_id, 
  DROP COLUMN IF EXISTS modified_by_id, DROP COLUMN IF EXISTS observer_id;
ALTER TABLE public.bin_observation 
  ADD COLUMN session_id BIGINT, ADD COLUMN deleted_by_session BIGINT, ADD COLUMN created_by_id BIGINT, 
  ADD COLUMN modified_by_id BIGINT, ADD COLUMN observer_id BIGINT;

-- EGG_OBSERVATION
ALTER TABLE public.egg_observation 
  DROP COLUMN IF EXISTS session_id, DROP COLUMN IF EXISTS egg_id, DROP COLUMN IF EXISTS deleted_by_session, 
  DROP COLUMN IF EXISTS created_by_id, DROP COLUMN IF EXISTS modified_by_id, DROP COLUMN IF EXISTS observer_id;
ALTER TABLE public.egg_observation 
  ADD COLUMN session_id BIGINT, ADD COLUMN egg_id BIGINT, ADD COLUMN deleted_by_session BIGINT, 
  ADD COLUMN created_by_id BIGINT, ADD COLUMN modified_by_id BIGINT, ADD COLUMN observer_id BIGINT;

-- HATCHLING_LEDGER
ALTER TABLE public.hatchling_ledger 
  DROP COLUMN IF EXISTS egg_id, DROP COLUMN IF EXISTS intake_id, DROP COLUMN IF EXISTS session_id;
ALTER TABLE public.hatchling_ledger 
  ADD COLUMN egg_id BIGINT, ADD COLUMN intake_id BIGINT, ADD COLUMN session_id BIGINT;

-- SYSTEM_LOG
ALTER TABLE public.system_log 
  DROP COLUMN IF EXISTS session_id, DROP COLUMN IF EXISTS observer_id;
ALTER TABLE public.system_log 
  ADD COLUMN session_id BIGINT, ADD COLUMN observer_id BIGINT;

-- ============================================================================
-- 4. RE-ESTABLISH ALL FOREIGN KEY CONSTRAINTS
-- ============================================================================

ALTER TABLE public.intake 
  ADD CONSTRAINT intake_species_id_fkey FOREIGN KEY (species_id) REFERENCES public.species(species_id),
  ADD CONSTRAINT intake_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id),
  ADD CONSTRAINT intake_observer_fkey FOREIGN KEY (created_by_id) REFERENCES public.observer(observer_id);

ALTER TABLE public.bin 
  ADD CONSTRAINT bin_intake_fkey FOREIGN KEY (intake_id) REFERENCES public.intake(intake_id),
  ADD CONSTRAINT bin_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id),
  ADD CONSTRAINT bin_observer_fkey FOREIGN KEY (created_by_id) REFERENCES public.observer(observer_id);

ALTER TABLE public.egg 
  ADD CONSTRAINT egg_bin_fkey FOREIGN KEY (bin_id) REFERENCES public.bin(bin_id),
  ADD CONSTRAINT egg_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id),
  ADD CONSTRAINT egg_observer_fkey FOREIGN KEY (created_by_id) REFERENCES public.observer(observer_id);

ALTER TABLE public.bin_observation 
  ADD CONSTRAINT bin_obs_bin_fkey FOREIGN KEY (bin_id) REFERENCES public.bin(bin_id),
  ADD CONSTRAINT bin_obs_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id),
  ADD CONSTRAINT bin_obs_observer_fkey FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);

ALTER TABLE public.egg_observation 
  ADD CONSTRAINT egg_obs_egg_fkey FOREIGN KEY (egg_id) REFERENCES public.egg(egg_id),
  ADD CONSTRAINT egg_obs_bin_fkey FOREIGN KEY (bin_id) REFERENCES public.bin(bin_id),
  ADD CONSTRAINT egg_obs_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id),
  ADD CONSTRAINT egg_obs_observer_fkey FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);

ALTER TABLE public.hatchling_ledger 
  ADD CONSTRAINT hatch_egg_fkey FOREIGN KEY (egg_id) REFERENCES public.egg(egg_id),
  ADD CONSTRAINT hatch_intake_fkey FOREIGN KEY (intake_id) REFERENCES public.intake(intake_id),
  ADD CONSTRAINT hatch_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id);

ALTER TABLE public.system_log 
  ADD CONSTRAINT sys_session_fkey FOREIGN KEY (session_id) REFERENCES public.session_log(session_id),
  ADD CONSTRAINT sys_observer_fkey FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);

-- ============================================================================
-- DONE
-- ============================================================================
COMMIT;
