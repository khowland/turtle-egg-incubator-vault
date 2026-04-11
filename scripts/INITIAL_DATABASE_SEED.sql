-- =============================================================================
-- SQL:        INITIAL_DATABASE_SEED.sql
-- Project:    Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
-- Standard:   Enforces Standard [§35, §36] (Singular, Snake_case, Contextual PKs)
-- Description: Clean-slate schema for production deployment to Supabase.
-- =============================================================================

BEGIN;

-- 1. [Registry] Clinical Observer Registry
CREATE TABLE IF NOT EXISTS public.observer (
    observer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    observer_name TEXT NOT NULL,
    role TEXT DEFAULT 'Staff',
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. [Registry] Shared Session Log
CREATE TABLE IF NOT EXISTS public.session_log (
    session_id TEXT PRIMARY KEY,
    observer_id UUID REFERENCES public.observer(observer_id),
    device_id TEXT,
    start_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_ping TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. [Lookup] Biological Species Registry
CREATE TABLE IF NOT EXISTS public.species (
    species_id TEXT PRIMARY KEY,
    species_name TEXT NOT NULL,
    species_code TEXT NOT NULL UNIQUE,
    intake_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. [Lookup] Development Stages (S0-S6)
CREATE TABLE IF NOT EXISTS public.development_stage (
    stage_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

-- 5. [Clinical] Maternal Case Ledger
CREATE TABLE IF NOT EXISTS public.mother (
    mother_id TEXT PRIMARY KEY DEFAULT 'M' || to_char(now(), 'YYYYMMDDHH24MISS'),
    mother_name TEXT NOT NULL,
    finder_turtle_name TEXT,
    species_id TEXT REFERENCES public.species(species_id),
    intake_date DATE DEFAULT CURRENT_DATE,
    intake_condition TEXT,
    notes TEXT,
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. [Clinical] Incubator Bin Registry
CREATE TABLE IF NOT EXISTS public.bin (
    bin_id TEXT PRIMARY KEY,
    mother_id TEXT REFERENCES public.mother(mother_id),
    harvest_date DATE DEFAULT CURRENT_DATE,
    total_eggs INTEGER,
    target_total_weight_g NUMERIC,
    substrate TEXT,
    shelf_location TEXT,
    bin_notes TEXT,
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. [Clinical] Biological Egg Ledger
CREATE TABLE IF NOT EXISTS public.egg (
    egg_id TEXT PRIMARY KEY,
    bin_id TEXT REFERENCES public.bin(bin_id),
    physical_mark INTEGER,
    current_stage TEXT REFERENCES public.development_stage(stage_id),
    status TEXT DEFAULT 'Active',
    egg_notes TEXT,
    session_id TEXT REFERENCES public.session_log(session_id),
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. [Sovereign Audit] Biological Observations
CREATE TABLE IF NOT EXISTS public.bin_observation (
    bin_observation_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES public.session_log(session_id),
    bin_id TEXT REFERENCES public.bin(bin_id),
    observer_id UUID REFERENCES public.observer(observer_id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    bin_weight_g NUMERIC,
    water_added_ml NUMERIC,
    env_notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id)
);

CREATE TABLE IF NOT EXISTS public.egg_observation (
    egg_observation_id BIGSERIAL PRIMARY KEY,
    session_id TEXT REFERENCES public.session_log(session_id),
    egg_id TEXT REFERENCES public.egg(egg_id),
    bin_id TEXT REFERENCES public.bin(bin_id),
    observer_id UUID REFERENCES public.observer(observer_id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    vascularity BOOLEAN,
    chalking INTEGER, -- 0-2 Scale
    molding BOOLEAN,
    leaking BOOLEAN,
    dented BOOLEAN DEFAULT FALSE,
    discolored BOOLEAN DEFAULT FALSE,
    moisture_deficit_g NUMERIC,
    water_added_ml NUMERIC,
    stage_at_observation TEXT,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id)
);

-- 9. [Final Outcome] Hatchling Outcome Ledger
CREATE TABLE IF NOT EXISTS public.hatchling_ledger (
    hatchling_ledger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id TEXT NOT NULL,
    mother_id TEXT NOT NULL,
    session_id TEXT,
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g NUMERIC,
    incubation_duration_days INTEGER,
    vitality_score TEXT,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. [System] Forensic Operational Log
CREATE TABLE IF NOT EXISTS public.system_log (
    system_log_id BIGSERIAL PRIMARY KEY,
    session_id TEXT,
    event_type TEXT,
    event_message TEXT,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- SEED DATA: Biological Registry & Lookups
-- =============================================================================

-- Populate Species Registry
INSERT INTO public.species (species_id, species_name, species_code, intake_count) VALUES
('BLA', 'Blandings Turtle', 'BLA', 0),
('SNAPP', 'Snapping Turtle', 'SNAPP', 0),
('PAINT', 'Painted Turtle', 'PAINT', 0),
('MAP', 'Map Turtle', 'MAP', 0),
('ORNA', 'Ornate Box Turtle', 'ORNA', 0),
('WOOD', 'Wood Turtle', 'WOOD', 0)
ON CONFLICT (species_id) DO NOTHING;

-- Populate Development Stages
INSERT INTO public.development_stage (stage_id, label, description) VALUES
('S0', 'Intake', 'Initial assessment and entry into the vault.'),
('S1', 'Pre-Vasc', 'Initial incubation period before veins visible.'),
('S2', 'Vascular', 'Network of veins clearly visible during candling.'),
('S3', 'Chalking', 'Visible calcium shell thickening.'),
('S4', 'Late Stage', 'Heavy vascularity or shadow movement.'),
('S5', 'Pipping', 'Physical breakthrough of the shell surface.'),
('S6', 'Hatched', 'Complete emergence; ready for transition.')
ON CONFLICT (stage_id) DO NOTHING;

-- Populate Initial Clinical Observers (Seed Users)
-- Note: Replace these with official WINC Staff Registry during first log-in.
INSERT INTO public.observer (observer_name, role) VALUES
('WINC Staff', 'Admin'),
('Volunteer Biologist', 'Staff')
ON CONFLICT DO NOTHING;

COMMIT;
