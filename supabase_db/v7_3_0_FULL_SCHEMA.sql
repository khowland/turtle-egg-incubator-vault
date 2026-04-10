-- =============================================================================
-- SQL:        v7_3_0_FULL_SCHEMA.sql (MASTER CONSOLIDATED)
-- Project:    Incubator Vault v7.3.0 — Wildlife In Need Center (WINC)
-- Author:     Antigravity (Audit Hardening Refactor)
-- Target:     Supabase (PostgreSQL 15+)
-- Description: Unified "One-Click" Ledger for fresh production deployment.
--             Includes 11-Species Registry, 7-Stage Audit Loop, and 
--             Resilient Session Recovery infrastructure.
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. INFRASTRUCTURE & GLOBAL FUNCTIONS
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- -----------------------------------------------------------------------------
-- 2. CORE REGISTRIES (Identity & Species)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.observer (
    observer_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'Volunteer',
    email TEXT,
    phone TEXT,
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

-- -----------------------------------------------------------------------------
-- 3. AUDIT & SESSION INFRASTRUCTURE
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.sessionlog (
    session_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    login_timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_agent TEXT
);

CREATE TABLE IF NOT EXISTS public.systemlog (
    log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES public.sessionlog(session_id),
    event_type TEXT NOT NULL, 
    event_message TEXT,
    payload JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 4. BIOLOGICAL LEDGER (Entities)
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.mother (
    mother_id TEXT PRIMARY KEY,
    mother_name TEXT NOT NULL,
    finder_turtle_name TEXT,
    species_id TEXT REFERENCES public.species(species_id),
    intake_date DATE NOT NULL DEFAULT CURRENT_DATE,
    condition TEXT,
    clinical_notes TEXT,
    notes TEXT,
    -- Audit Header §6.59
    session_id TEXT REFERENCES public.sessionlog(session_id),
    created_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    modified_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.bin (
    bin_id TEXT PRIMARY KEY,
    mother_id TEXT REFERENCES public.mother(mother_id) ON DELETE CASCADE,
    harvest_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_eggs INTEGER,
    target_total_weight_g DECIMAL(10,2),
    shelf_location TEXT,
    substrate TEXT,
    -- Audit Header §6.59
    session_id TEXT REFERENCES public.sessionlog(session_id),
    created_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    modified_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.egg (
    egg_id TEXT PRIMARY KEY,
    bin_id TEXT REFERENCES public.bin(bin_id) ON DELETE CASCADE,
    physical_mark INTEGER,
    mark_description TEXT,
    current_stage TEXT DEFAULT 'S0',
    status TEXT DEFAULT 'Active', -- Active, Dead, Transferred
    -- Audit Header §6.59
    session_id TEXT REFERENCES public.sessionlog(session_id),
    created_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    modified_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 5. TELEMETRY & OBSERVATION
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.development_stage (
    stage_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS public.eggobservation (
    detail_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES public.sessionlog(session_id),
    egg_id TEXT REFERENCES public.egg(egg_id),
    observer_id TEXT REFERENCES public.observer(observer_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    vascularity BOOLEAN DEFAULT FALSE,
    chalking INTEGER DEFAULT 0,
    molding BOOLEAN DEFAULT FALSE,
    leaking BOOLEAN DEFAULT FALSE,
    dented BOOLEAN DEFAULT FALSE,
    discolored BOOLEAN DEFAULT FALSE,
    moisture_deficit_g DECIMAL(10,2),
    water_added_ml DECIMAL(10,2),
    stage_at_observation TEXT,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.incubatorobservation (
    obs_id TEXT PRIMARY KEY,
    session_id TEXT REFERENCES public.sessionlog(session_id),
    bin_id TEXT REFERENCES public.bin(bin_id),
    observer_id TEXT REFERENCES public.observer(observer_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    observer_name TEXT,
    bin_weight_g DECIMAL(10,2),
    water_added_ml DECIMAL(10,2),
    ambient_temp NUMERIC,
    humidity NUMERIC,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.hatchling_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id TEXT NOT NULL,
    mother_id TEXT NOT NULL,
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g DECIMAL(10,2),
    incubation_duration_days INTEGER,
    vitality_score TEXT,
    notes TEXT,
    -- Audit Header §6.59
    session_id TEXT REFERENCES public.sessionlog(session_id),
    created_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    modified_by_id TEXT REFERENCES public.observer(observer_id) ON DELETE SET NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    modified_at TIMESTAMPTZ DEFAULT NOW()
);

-- -----------------------------------------------------------------------------
-- 6. DYNAMIC LOOKUP DATA (SEEDING)
-- -----------------------------------------------------------------------------

-- Species Registry (11 Wisconsin Native Species)
INSERT INTO public.species (species_id, common_name, scientific_name, species_code, vulnerability_status)
VALUES 
    ('BL', 'Blanding’s Turtle', 'Emydoidea blandingii', 'BL', 'Endangered (WI)'),
    ('WT', 'Wood Turtle', 'Glyptemys insculpta', 'WT', 'Threatened (WI)'),
    ('OB', 'Ornate Box Turtle', 'Terrapene ornata', 'OB', 'Endangered (WI)'),
    ('PA', 'Painted Turtle', 'Chrysemys picta', 'PA', 'Common'),
    ('SN', 'Snapping Turtle', 'Chelydra serpentina', 'SN', 'Common'),
    ('MT', 'Common Map Turtle', 'Graptemys geographica', 'MT', 'Common'),
    ('FM', 'False Map Turtle', 'Graptemys pseudogeographica', 'FM', 'Common'),
    ('OM', 'Ouachita Map Turtle', 'Graptemys ouachitensis', 'OM', 'Common'),
    ('SS', 'Spiny Softshell', 'Apalone spinifera', 'SS', 'Common'),
    ('SM', 'Smooth Softshell', 'Apalone mutica', 'SM', 'Special Concern'),
    ('MK', 'Musk Turtle', 'Sternotherus odoratus', 'MK', 'Common')
ON CONFLICT (species_id) DO NOTHING;

-- Development Stages
INSERT INTO public.development_stage (stage_id, label) 
VALUES 
    ('S0', 'Intake'), ('S1', 'Warming'), ('S2', 'Development'), 
    ('S3', 'Established'), ('S4', 'Mature'), ('S5', 'Pipping'), ('S6', 'Hatched')
ON CONFLICT (stage_id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 7. CLUE CHAIN AUTOMATION (Triggers)
-- -----------------------------------------------------------------------------

-- Mother ID Generation
CREATE OR REPLACE FUNCTION generate_mother_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.mother_id IS NULL THEN
        NEW.mother_id := REPLACE(NEW.mother_name, ' ', '') || '_' || 
                         NEW.species_id || '_' || 
                         TO_CHAR(NEW.intake_date, 'YYYYMMDD');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_generate_mother_id 
    BEFORE INSERT ON public.mother 
    FOR EACH ROW EXECUTE FUNCTION generate_mother_id();

-- Observation ID Generation
CREATE OR REPLACE FUNCTION generate_obs_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.obs_id IS NULL THEN
        NEW.obs_id := NEW.session_id || '_ENV_' || TO_CHAR(NEW.timestamp, 'HH24MISS');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_generate_obs_id 
    BEFORE INSERT ON public.incubatorobservation 
    FOR EACH ROW EXECUTE FUNCTION generate_obs_id();

-- Global Modified_At Trigger
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LOOP
        IF t NOT IN ('sessionlog', 'systemlog', 'development_stage') THEN
            EXECUTE format('CREATE TRIGGER update_%I_modtime BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_modified_column()', t, t);
        END IF;
    END LOOP;
END $$;

COMMIT;
