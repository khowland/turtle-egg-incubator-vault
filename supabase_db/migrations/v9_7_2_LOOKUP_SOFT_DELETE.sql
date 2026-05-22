-- ═══════════════════════════════════════════════════════════════
-- Migration: v9_7_2
-- Purpose: Add is_deleted column to lookup tables for soft-delete
--          compliance per §4 Resilience & Security mandate.
-- Date:    2026-05-22
-- ═══════════════════════════════════════════════════════════════

BEGIN;

-- Add is_deleted to species lookup table
ALTER TABLE public.species 
  ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT false;

-- Add is_deleted to development_stage lookup table
ALTER TABLE public.development_stage 
  ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT false;

-- Add is_deleted to biological_property lookup table
ALTER TABLE public.biological_property 
  ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT false;

-- Bump APP_VERSION
UPDATE public.system_config 
SET config_value = 'v9.7.2', modified_at = NOW() 
WHERE config_name = 'APP_VERSION';

COMMIT;
