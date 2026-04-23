-- =============================================================================
-- SQL:        v8_1_15_ADD_AUDIT_TO_BIN.sql
-- Project:    Incubator Vault v8.1.15
-- Purpose:    Adds missing audit columns to 'bin' to satisfy modern triggers.
-- =============================================================================

BEGIN;

-- 1. Add audit columns to bin
ALTER TABLE public.bin 
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

COMMIT;

-- Success row
SELECT 'Success' AS status, 'Audit columns created_at and modified_at added to table bin.' AS message;
