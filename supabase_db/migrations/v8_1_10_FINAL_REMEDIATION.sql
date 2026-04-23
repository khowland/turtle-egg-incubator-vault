-- =============================================================================
-- SQL:        v8_1_10_FINAL_REMEDIATION.sql
-- Project:    Incubator Vault v8.1.10
-- Purpose:    Rewrites legacy ID generation functions to use 'intake_id'.
-- =============================================================================

BEGIN;

-- 1. Drop the legacy trigger first
DROP TRIGGER IF EXISTS tr_generate_mother_id ON public.intake;

-- 2. Rewrite generate_mother_id -> generate_intake_id
CREATE OR REPLACE FUNCTION public.generate_intake_id()
 RETURNS trigger
 LANGUAGE plpgsql
 AS $function$
 BEGIN
     -- Respect existing IDs if provided (essential for our validation runner)
     IF NEW.intake_id IS NULL THEN
         NEW.intake_id := 'I' || REPLACE(COALESCE(NEW.intake_name, 'UNK'), ' ', '') || '_' || 
                          NEW.species_id || '_' || 
                          TO_CHAR(NEW.intake_date, 'YYYYMMDD');
     END IF;
     RETURN NEW;
 END;
 $function$;

-- 3. Rewrite generate_bin_id to use intake_id
CREATE OR REPLACE FUNCTION public.generate_bin_id()
 RETURNS trigger
 LANGUAGE plpgsql
 AS $function$
 DECLARE
     next_bin_num INTEGER;
 BEGIN
     IF NEW.bin_id IS NULL THEN
         SELECT COALESCE(COUNT(*), 0) + 1 INTO next_bin_num 
         FROM public.bin 
         WHERE intake_id = NEW.intake_id;
         
         NEW.bin_id := NEW.intake_id || '_B' || next_bin_num;
     END IF;
     RETURN NEW;
 END;
 $function$;

-- 4. Re-establish the triggers with modern names
CREATE TRIGGER tr_generate_intake_id 
    BEFORE INSERT ON public.intake 
    FOR EACH ROW EXECUTE FUNCTION public.generate_intake_id();

-- (Note: generate_bin_id trigger is likely already named tr_generate_bin_id on the bin table)
-- We ensure its definition is updated by the CREATE OR REPLACE FUNCTION above.

COMMIT;

-- Success verification row
SELECT 'Success' AS status, 'Legacy ID generation synchronized with modern Intake schema.' AS message;
