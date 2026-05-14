-- =============================================================================
-- SQL:        v8_1_23_REMEDIATE_SCHEMA_DESYNC.sql
-- Project:    Incubator Vault v8.1.23
-- Purpose:    Emergency remediation of missing audit columns and triggers.
--             Resolves "Bio-Ledger Error" on User Sync.
-- =============================================================================

BEGIN;

-- 1. [Registry] Observer
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'observer' AND column_name = 'modified_at') THEN
        ALTER TABLE public.observer ADD COLUMN modified_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- 2. [Clinical] Bin
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bin' AND column_name = 'modified_at') THEN
        ALTER TABLE public.bin ADD COLUMN modified_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- 3. [Clinical] Bin Observation
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bin_observation' AND column_name = 'modified_at') THEN
        ALTER TABLE public.bin_observation ADD COLUMN modified_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- 4. [Clinical] Egg Observation
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'modified_at') THEN
        ALTER TABLE public.egg_observation ADD COLUMN modified_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- 5. [Triggers] Re-establish Standard Sync Function if missing
CREATE OR REPLACE FUNCTION public.sync_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 6. [Triggers] Re-apply to Observer
DROP TRIGGER IF EXISTS tr_observer_modified_at ON public.observer;
CREATE TRIGGER tr_observer_modified_at
    BEFORE UPDATE ON public.observer
    FOR EACH ROW EXECUTE FUNCTION public.sync_modified_at();

-- 7. [Triggers] Re-apply to Observations
DROP TRIGGER IF EXISTS tr_bin_obs_modified_at ON public.bin_observation;
CREATE TRIGGER tr_bin_obs_modified_at
    BEFORE UPDATE ON public.bin_observation
    FOR EACH ROW EXECUTE FUNCTION public.sync_modified_at();

DROP TRIGGER IF EXISTS tr_egg_obs_modified_at ON public.egg_observation;
CREATE TRIGGER tr_egg_obs_modified_at
    BEFORE UPDATE ON public.egg_observation
    FOR EACH ROW EXECUTE FUNCTION public.sync_modified_at();

COMMIT;

-- Success Row
SELECT 'Success' AS status, 'Schema desync remediated for observer and observation tables.' AS message;
