-- =============================================================================
-- SQL:        v8_1_9_SEARCH_LEAKS.sql
-- Project:    Incubator Vault v8.1.9
-- Purpose:    Forensic Search for all 'mother_id' references in the schema.
--             Run this in the Supabase SQL Editor to find the leak!
-- =============================================================================

-- Search Functions, Triggers, and Views for the pattern 'mother_id'
WITH leaks AS (
    -- 1. Search Functions
    SELECT 
        'FUNCTION' as type,
        p.proname as name,
        pg_get_functiondef(p.oid) as definition
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
      AND p.prokind != 'a' -- Skip aggregate functions
      AND pg_get_functiondef(p.oid) ~* 'mother_id'

    UNION ALL

    -- 2. Search Triggers
    SELECT 
        'TRIGGER' as type,
        t.tgname as name,
        pg_get_triggerdef(t.oid) as definition
    FROM pg_trigger t
    JOIN pg_class c ON c.oid = t.tgrelid
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'public'
      AND pg_get_triggerdef(t.oid) ~* 'mother_id'

    UNION ALL

    -- 3. Search Views
    SELECT 
        'VIEW' as type,
        viewname as name,
        definition
    FROM pg_views
    WHERE schemaname = 'public'
      AND definition ~* 'mother_id'
)
SELECT * FROM leaks;
