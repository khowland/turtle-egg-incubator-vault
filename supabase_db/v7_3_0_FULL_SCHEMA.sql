-- =============================================================================
-- SQL:        v7_3_0_FULL_SCHEMA.sql (ENTERPRISE CONSOLIDATED)
-- Project:    Incubator Vault v7.3.0 — Wildlife In Need Center (WINC)
-- Author:     Antigravity (Titan Engine Standard Alignment)
-- Target:     Supabase (PostgreSQL 15+)
-- Description: Unified "One-Click" Ledger for fresh production deployment.
--             Strictly enforces §35 Enterprise Naming Standards with UUID parity.
-- =============================================================================

BEGIN;

-- 1. Infrastructure Helpers
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Core Registries
CREATE TABLE IF NOT EXISTS public.observer (
    observer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'Volunteer',
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.species (
    species_id TEXT PRIMARY KEY,
    species_code CHAR(2) UNIQUE NOT NULL,
    common_name TEXT NOT NULL UNIQUE,
    scientific_name TEXT NOT NULL UNIQUE,
    vulnerability_status TEXT,
    intake_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Audit & Session Foundation
CREATE TABLE IF NOT EXISTS public.session_log (
    session_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    login_timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_agent TEXT
);

CREATE TABLE IF NOT EXISTS public.system_log (
    system_log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES public.session_log(session_id),
    event_type TEXT NOT NULL, 
    event_message TEXT,
    payload JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Biological Entities
CREATE TABLE IF NOT EXISTS public.mother (
    mother_id TEXT PRIMARY KEY,
    mother_name TEXT NOT NULL,
    species_id TEXT REFERENCES public.species(species_id),
    intake_date DATE NOT NULL DEFAULT CURRENT_DATE,
    finder_turtle_name TEXT,
    intake_condition TEXT,
    extraction_method TEXT,
    discovery_location TEXT,
    carapace_length_mm DECIMAL(10,2),
    condition TEXT,
    notes TEXT,
    -- Audit Header §35.4
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.bin (
    bin_id TEXT PRIMARY KEY,
    mother_id TEXT REFERENCES public.mother(mother_id) ON DELETE CASCADE,
    total_eggs INTEGER,
    target_total_weight_g DECIMAL(10,2),
    shelf_location TEXT,
    substrate TEXT,
    bin_notes TEXT,
    -- Audit Header §35.4
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.egg (
    egg_id TEXT PRIMARY KEY,
    bin_id TEXT REFERENCES public.bin(bin_id) ON DELETE CASCADE,
    physical_mark INTEGER,
    status TEXT DEFAULT 'Active',
    current_stage TEXT DEFAULT 'S0',
    intake_date DATE,
    egg_notes TEXT,
    last_chalk INTEGER,
    last_vasc BOOLEAN,
    -- Audit Header §35.4
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Observations
CREATE TABLE IF NOT EXISTS public.egg_observation (
    egg_observation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES public.session_log(session_id),
    egg_id TEXT REFERENCES public.egg(egg_id),
    bin_id TEXT REFERENCES public.bin(bin_id),
    observer_id UUID REFERENCES public.observer(observer_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    egg_observation_date DATE DEFAULT CURRENT_DATE, -- Clinical Backdating (§4.D)
    vascularity BOOLEAN DEFAULT FALSE,
    chalking INTEGER DEFAULT 0,
    molding BOOLEAN DEFAULT FALSE,
    leaking BOOLEAN DEFAULT FALSE,
    dented BOOLEAN DEFAULT FALSE,
    discolored BOOLEAN DEFAULT FALSE,
    moisture_deficit_g DECIMAL(10,2),
    water_added_ml DECIMAL(10,2),
    observation_notes TEXT,
    stage_at_observation TEXT,
    void_reason TEXT,
    -- Audit Header §35.4
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.bin_observation (
    bin_observation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT REFERENCES public.session_log(session_id),
    bin_id TEXT REFERENCES public.bin(bin_id),
    observer_id UUID REFERENCES public.observer(observer_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    bin_weight_g DECIMAL(10,2),
    water_added_ml DECIMAL(10,2),
    env_notes TEXT,
    -- Audit Header §35.4
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.hatchling_ledger (
    hatchling_ledger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id TEXT NOT NULL,
    mother_id TEXT NOT NULL,
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g DECIMAL(10,2),
    vitality_score TEXT,
    incubation_duration_days INTEGER,
    notes TEXT,
    -- Audit Header §35.4
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Seed Data
INSERT INTO public.species (species_id, common_name, scientific_name, species_code)
VALUES 
    ('BL', 'Blanding’s Turtle', 'Emydoidea blandingii', 'BL'),
    ('WT', 'Wood Turtle', 'Glyptemys insculpta', 'WT'),
    ('PA', 'Painted Turtle', 'Chrysemys picta', 'PA'),
    ('SN', 'Snapping Turtle', 'Chelydra serpentina', 'SN'),
    ('MK', 'Musk Turtle', 'Sternotherus odoratus', 'MK')
ON CONFLICT (species_id) DO NOTHING;

COMMIT;
