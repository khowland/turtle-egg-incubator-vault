-- =============================================================================
-- SQL:        v8_1_8_HARD_RESET_TRIGGERS.sql
-- Project:    Incubator Vault v8.1.8
-- Purpose:    Dynamically drops ALL triggers on critical clinical tables to 
--             purge hidden legacy functions that reference 'mother_id'.
-- =============================================================================

DO $$ 
DECLARE 
    r RECORD;
BEGIN
    -- 1. Drop ALL triggers on 'intake'
    FOR r IN (SELECT tgname FROM pg_trigger JOIN pg_class ON pg_class.oid = tgrelid WHERE relname = 'intake' AND NOT tgisinternal) LOOP
        EXECUTE 'DROP TRIGGER ' || r.tgname || ' ON intake';
    END LOOP;
    
    -- 2. Drop ALL triggers on 'bin'
    FOR r IN (SELECT tgname FROM pg_trigger JOIN pg_class ON pg_class.oid = tgrelid WHERE relname = 'bin' AND NOT tgisinternal) LOOP
        EXECUTE 'DROP TRIGGER ' || r.tgname || ' ON bin';
    END LOOP;
    
    -- 3. Drop ALL triggers on 'egg'
    FOR r IN (SELECT tgname FROM pg_trigger JOIN pg_class ON pg_class.oid = tgrelid WHERE relname = 'egg' AND NOT tgisinternal) LOOP
        EXECUTE 'DROP TRIGGER ' || r.tgname || ' ON egg';
    END LOOP;
END $$;

-- 4. Re-establish modern audit triggers
CREATE OR REPLACE FUNCTION public.sync_modified_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_intake_modified_at
    BEFORE UPDATE ON public.intake
    FOR EACH ROW EXECUTE FUNCTION public.sync_modified_at();

CREATE TRIGGER tr_bin_modified_at
    BEFORE UPDATE ON public.bin
    FOR EACH ROW EXECUTE FUNCTION public.sync_modified_at();

CREATE TRIGGER tr_egg_modified_at
    BEFORE UPDATE ON public.egg
    FOR EACH ROW EXECUTE FUNCTION public.sync_modified_at();

-- Success Row for User Feedback
SELECT 'Success' AS status, 'All legacy triggers purged and modern audit re-established.' AS message;
