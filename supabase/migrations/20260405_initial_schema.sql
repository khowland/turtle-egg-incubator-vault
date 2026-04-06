/* 
  INCUBATOR VAULT v2.0 - INITIAL RELATIONAL SCHEMA
  Author: Antigravity (Agent Zero Persona)
  Target: Supabase (PostgreSQL 15+)
*/

-- 1. SETUP AUDIT & SESSION INFRASTRUCTURE
CREATE TABLE IF NOT EXISTS public.SessionLog (
    session_id TEXT PRIMARY KEY, /* [UserShortName]_[YYYYMMDDHHMMSS] */
    user_name TEXT NOT NULL,
    login_timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_agent TEXT
);

CREATE TABLE IF NOT EXISTS public.SystemLog (
    log_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES public.SessionLog(session_id),
    event_type TEXT NOT NULL, /* SESSION_START, ERROR, TRACE, AUTH, DELETE, DATA_CHANGE */
    event_message TEXT,
    payload JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- 2. BIOLOGICAL ASSETS
CREATE TABLE IF NOT EXISTS public.species (
    species_id TEXT PRIMARY KEY, /* "Blandings", "Wood", "Ornate", etc. */
    common_name TEXT NOT NULL UNIQUE,
    scientific_name TEXT NOT NULL UNIQUE,
    incubation_min_days INTEGER,
    incubation_max_days INTEGER,
    optimal_temp_low NUMERIC,
    optimal_temp_high NUMERIC,
    vulnerability_status TEXT
);

CREATE TABLE IF NOT EXISTS public.mother (
    mother_id TEXT PRIMARY KEY, /* [MotherName]_[Species]_[YYYYMMDD] */
    mother_name TEXT NOT NULL,
    species_id TEXT REFERENCES public.species(species_id),
    intake_date DATE NOT NULL DEFAULT CURRENT_DATE,
    condition TEXT,
    notes TEXT,
    created_by_session TEXT REFERENCES public.SessionLog(session_id),
    updated_by_session TEXT REFERENCES public.SessionLog(session_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES public.SessionLog(session_id)
);

CREATE TABLE IF NOT EXISTS public.bin (
    bin_id TEXT PRIMARY KEY, /* [MotherID]_B[Number] */
    mother_id TEXT REFERENCES public.mother(mother_id),
    harvest_date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_eggs INTEGER CHECK (total_eggs <= 300), -- Increased from 276 for safety
    created_by_session TEXT REFERENCES public.SessionLog(session_id),
    updated_by_session TEXT REFERENCES public.SessionLog(session_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES public.SessionLog(session_id)
);

CREATE TABLE IF NOT EXISTS public.egg (
    egg_id TEXT PRIMARY KEY, /* [BinID]_E[Number] */
    bin_id TEXT REFERENCES public.bin(bin_id),
    physical_mark INTEGER,
    current_stage TEXT DEFAULT 'Intake', /* Intake, Developing, Established, Mature, Pipping, Hatched */
    status TEXT DEFAULT 'Active', /* Active, Dead, Hatched */
    created_by_session TEXT REFERENCES public.SessionLog(session_id),
    updated_by_session TEXT REFERENCES public.SessionLog(session_id),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES public.SessionLog(session_id)
);

-- 3. TELEMETRY & OBSERVATION
CREATE TABLE IF NOT EXISTS public.IncubatorObservation (
    obs_id TEXT PRIMARY KEY, /* [SessionID]_ENV_[HHMMSS] */
    session_id TEXT REFERENCES public.SessionLog(session_id),
    bin_id TEXT REFERENCES public.bin(bin_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    observer_name TEXT NOT NULL,
    ambient_temp NUMERIC,
    humidity NUMERIC,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES public.SessionLog(session_id)
);

CREATE TABLE IF NOT EXISTS public.EggObservation (
    detail_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    session_id TEXT REFERENCES public.SessionLog(session_id),
    egg_id TEXT REFERENCES public.egg(egg_id),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    vascularity BOOLEAN,
    chalking INTEGER CHECK (chalking BETWEEN 0 AND 2),
    molding BOOLEAN,
    leaking BOOLEAN,
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by_session TEXT REFERENCES public.SessionLog(session_id)
);

-- 4. CLUE CHAIN TRIGGERS (PL/pgSQL)

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

-- Bin ID Generation
CREATE OR REPLACE FUNCTION generate_bin_id()
RETURNS TRIGGER AS $$
DECLARE
    next_bin_num INTEGER;
BEGIN
    IF NEW.bin_id IS NULL THEN
        SELECT COALESCE(COUNT(*), 0) + 1 INTO next_bin_num 
        FROM public.bin 
        WHERE mother_id = NEW.mother_id;
        
        NEW.bin_id := NEW.mother_id || '_B' || next_bin_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_generate_bin_id
BEFORE INSERT ON public.bin
FOR EACH ROW EXECUTE FUNCTION generate_bin_id();

-- Egg ID Generation
CREATE OR REPLACE FUNCTION generate_egg_id()
RETURNS TRIGGER AS $$
DECLARE
    next_egg_num INTEGER;
BEGIN
    IF NEW.egg_id IS NULL THEN
        SELECT COALESCE(COUNT(*), 0) + 1 INTO next_egg_num 
        FROM public.egg 
        WHERE bin_id = NEW.bin_id;
        
        NEW.egg_id := NEW.bin_id || '_E' || next_egg_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_generate_egg_id
BEFORE INSERT ON public.egg
FOR EACH ROW EXECUTE FUNCTION generate_egg_id();

-- Environment Obs ID Generation
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
BEFORE INSERT ON public.IncubatorObservation
FOR EACH ROW EXECUTE FUNCTION generate_obs_id();

-- 5. BIOLOGIST SEEDING (WISCONSIN SPECIES)
INSERT INTO public.species (species_id, common_name, scientific_name, incubation_min_days, incubation_max_days, optimal_temp_low, optimal_temp_high, vulnerability_status)
VALUES 
('Blandings', 'Blanding’s Turtle', 'Emydoidea blandingii', 65, 90, 80, 84, 'Endangered (WI)'),
('Wood', 'Wood Turtle', 'Glyptemys insculpta', 60, 80, 78, 82, 'Threatened (WI)'),
('Ornate', 'Ornate Box Turtle', 'Terrapene ornata', 60, 75, 80, 85, 'Endangered (WI)'),
('Painted', 'Painted Turtle', 'Chrysemys picta', 50, 80, 75, 82, 'Common'),
('Snapping', 'Snapping Turtle', 'Chelydra serpentina', 80, 90, 75, 82, 'Common'),
('Map', 'Grape Turtle', 'Graptemys geographica', 55, 75, 80, 83, 'Common')
ON CONFLICT (species_id) DO NOTHING;
