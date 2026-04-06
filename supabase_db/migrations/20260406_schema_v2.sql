-- =============================================================================
-- Migration: 20260406_schema_v2.sql
-- Project:   Incubator Vault v6.0 — Wildlife In Need Center (WINC)
-- Purpose:   Implement observer/incubator registries and expand core tables
--            per Requirements.md v6.0.
-- =============================================================================

-- 1. CREATE OBSERVER REGISTRY
CREATE TABLE IF NOT EXISTS public.observer (
    observer_id TEXT PRIMARY KEY, -- Slug: "elisa", "kevin"
    display_name TEXT NOT NULL,
    role TEXT NOT NULL, -- Lead, Staff, Volunteer
    email TEXT,
    phone TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. CREATE INCUBATOR REGISTRY
CREATE TABLE IF NOT EXISTS public.incubator (
    incubator_id TEXT PRIMARY KEY, -- "INC-01"
    label TEXT NOT NULL,
    location TEXT,
    target_temp NUMERIC,
    target_humidity NUMERIC,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. EXPAND MOTHER TABLE
ALTER TABLE public.mother 
ADD COLUMN IF NOT EXISTS harvest_location TEXT,
ADD COLUMN IF NOT EXISTS gps_lat NUMERIC,
ADD COLUMN IF NOT EXISTS gps_lon NUMERIC,
ADD COLUMN IF NOT EXISTS clinical_notes TEXT;

-- 4. EXPAND BIN TABLE
ALTER TABLE public.bin 
ADD COLUMN IF NOT EXISTS incubator_id TEXT REFERENCES public.incubator(incubator_id),
ADD COLUMN IF NOT EXISTS substrate TEXT,
ADD COLUMN IF NOT EXISTS bin_label TEXT;

-- 5. EXPAND EGG TABLE
ALTER TABLE public.egg 
ADD COLUMN IF NOT EXISTS mark_description TEXT;

-- 6. EXPAND EGG OBSERVATION
ALTER TABLE public.EggObservation 
ADD COLUMN IF NOT EXISTS dented BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS discolored BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS observer_id TEXT REFERENCES public.observer(observer_id),
ADD COLUMN IF NOT EXISTS stage_at_observation TEXT;

-- 7. EXPAND INCUBATOR OBSERVATION
ALTER TABLE public.IncubatorObservation 
ADD COLUMN IF NOT EXISTS incubator_id TEXT REFERENCES public.incubator(incubator_id),
ADD COLUMN IF NOT EXISTS observer_id TEXT REFERENCES public.observer(observer_id);

-- 8. SEED INITIAL DATA
INSERT INTO public.observer (observer_id, display_name, role)
VALUES 
('elisa', 'Elisa Rodriguez', 'Lead'),
('kevin', 'Kevin Howland', 'Staff')
ON CONFLICT (observer_id) DO NOTHING;

INSERT INTO public.incubator (incubator_id, label, location, target_temp, target_humidity)
VALUES 
('INC-01', 'Incubator Alpha', 'Lab Room A, Shelf 2', 82.0, 80.0),
('INC-02', 'Incubator Beta', 'Lab Room A, Shelf 3', 80.0, 75.0)
ON CONFLICT (incubator_id) DO NOTHING;
