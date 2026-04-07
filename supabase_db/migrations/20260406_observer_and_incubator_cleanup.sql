-- =============================================================================
-- Migration: 20260406_observer_and_incubator_cleanup.sql
-- Purpose:   Formalize observer table and remove incubator unit tracking.
-- Author:    Agent Zero
-- =============================================================================

-- 1. Formalize Observer Table
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

-- 2. Cleanup Incubator Table and References
-- Remove foreign keys first
ALTER TABLE IF EXISTS public.bin DROP COLUMN IF EXISTS incubator_id;
ALTER TABLE IF EXISTS public.incubatorobservation DROP COLUMN IF EXISTS incubator_id;

-- Drop the incubator table
DROP TABLE IF EXISTS public.incubator CASCADE;

-- 3. Seed Observers (Ensure these exist)
INSERT INTO public.observer (observer_id, display_name, role)
VALUES 
    ('elisa', 'Elisa Rodriguez', 'Lead'),
    ('kevin', 'Kevin Howland', 'Staff')
ON CONFLICT (observer_id) DO UPDATE SET 
    display_name = EXCLUDED.display_name, 
    role = EXCLUDED.role;
