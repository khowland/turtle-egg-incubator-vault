-- Migration: 20260406_observer_formalization.sql
-- Formalizes observer table and removes incubator tracking.

CREATE TABLE IF NOT EXISTS public.observer (
    observer_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'Volunteer',
    email TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Drop incubator unit complexity
ALTER TABLE IF EXISTS public.bin DROP COLUMN IF EXISTS incubator_id;
DROP TABLE IF EXISTS public.incubator CASCADE;

INSERT INTO public.observer (observer_id, display_name, role)
VALUES 
    ('elisa', 'Elisa Rodriguez', 'Lead'),
    ('kevin', 'Kevin Howland', 'Staff')
ON CONFLICT (observer_id) DO NOTHING;
