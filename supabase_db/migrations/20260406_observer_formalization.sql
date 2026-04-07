-- =============================================================================
-- Migration: 20260406_observer_formalization.sql
-- Purpose:   Formalize observer table and remove incubator unit tracking.
-- Author:    Agent Zero
-- =============================================================================

-- 1. Create Observer Table (User Registry)
CREATE TABLE IF NOT EXISTS public.observer (
    observer_id TEXT PRIMARY KEY, -- Slug: "elisa"
    display_name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'Volunteer', -- Lead, Staff, Volunteer
    email TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Clean up Incubator References from existing tables
-- Bin table: Remove incubator_id FK and column
ALTER TABLE IF EXISTS public.bin DROP COLUMN IF EXISTS incubator_id;

-- IncubatorObservation: Remove incubator_id and rename table for generic environment logging
ALTER TABLE IF EXISTS public.incubatorobservation DROP COLUMN IF EXISTS incubator_id;

-- Drop the incubator table (Lookup table)
DROP TABLE IF EXISTS public.incubator CASCADE;

-- 3. Seed Initial Observers
INSERT INTO public.observer (observer_id, display_name, role)
VALUES 
    ('elisa', 'Elisa Rodriguez', 'Lead'),
    ('kevin', 'Kevin Howland', 'Staff')
ON CONFLICT (observer_id) DO NOTHING;
