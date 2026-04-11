-- =============================================================================
-- SQL:        v8_1_1_FULL_PRODUCTION_SCHEMA.sql
-- Project:    Incubator Vault v8.1.1 — WINC (Clinical Sovereignty Edition)
-- Standard:   Industry Best Practice (Sovereign Mesh v8.1.1)
-- Description: Consolidated primary ledger schema and lookup seed data.
-- =============================================================================

BEGIN;

-- 1. [Registry] Clinical Observer Registry
CREATE TABLE IF NOT EXISTS public.observer (
    observer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    observer_name TEXT NOT NULL,
    role TEXT DEFAULT 'Staff',
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. [Registry] Shared Session Log
CREATE TABLE IF NOT EXISTS public.session_log (
    session_id TEXT PRIMARY KEY,
    user_name TEXT, -- Captures the display name of the observer who started/adopted the session
    user_agent TEXT,
    login_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. [Lookup] Biological Species Registry
CREATE TABLE IF NOT EXISTS public.species (
    species_id TEXT PRIMARY KEY,
    species_name TEXT NOT NULL,
    species_code TEXT NOT NULL UNIQUE,
    intake_count INTEGER DEFAULT 0,
    common_name TEXT,
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
    mother_id TEXT PRIMARY KEY, -- Standard v8: String-based ID logic (e.g. M20260411...)
    mother_name TEXT NOT NULL,
    finder_turtle_name TEXT,
    species_id TEXT REFERENCES public.species(species_id),
    intake_date DATE DEFAULT CURRENT_DATE,
    intake_condition TEXT,
    extraction_method TEXT,
    discovery_location TEXT,
    carapace_length_mm NUMERIC,
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
    intake_date DATE,
    egg_notes TEXT,
    last_chalk INTEGER,
    last_vasc BOOLEAN,
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
    void_reason TEXT,
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
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_id UUID REFERENCES public.observer(observer_id),
    modified_by_id UUID REFERENCES public.observer(observer_id)
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
INSERT INTO public.species (species_id, species_name, species_code, common_name, intake_count) VALUES
('BL', 'Blanding''s Turtle', 'BL', 'Blanding''s Turtle', 0),
('WT', 'Wood Turtle', 'WT', 'Wood Turtle', 0),
('OB', 'Ornate Box Turtle', 'OB', 'Ornate Box Turtle', 0),
('PA', 'Painted Turtle', 'PA', 'Painted Turtle', 0),
('SN', 'Snapping Turtle', 'SN', 'Snapping Turtle', 0),
('MT', 'Map Turtle', 'MT', 'Map Turtle', 0),
('FM', 'False Map Turtle', 'FM', 'False Map Turtle', 0),
('OM', 'Ouachita Map Turtle', 'OM', 'Ouachita Map Turtle', 0),
('SS', 'Smooth Softshell', 'SS', 'Smooth Softshell', 0),
('SM', 'Spiny Softshell', 'SM', 'Spiny Softshell', 0),
('MK', 'Musk Turtle', 'MK', 'Musk Turtle', 0)
ON CONFLICT (species_id) DO NOTHING;

-- Populate Development Stages
INSERT INTO public.development_stage (stage_id, label, description) VALUES
('S0', 'Intake', 'Initial assessment and entry into the vault.'),
('S1', 'Early Dev', 'Initial incubation period; no vascularity visible.'),
('S2', 'Vascular', 'Network of veins clearly visible during candling.'),
('S3', 'Chalking', 'Visible calcium shell thickening.'),
('S4', 'Late Stage', 'Heavy vascularity or shadow movement; yolk absorption start.'),
('S5', 'Pipping', 'Physical breakthrough of the shell surface.'),
('S6', 'Hatched', 'Complete emergence; ready for transition.')
ON CONFLICT (stage_id) DO NOTHING;

-- Populate Initial Clinical Observers (Seed Users)
INSERT INTO public.observer (observer_name, role) VALUES
('WINC Staff', 'Admin'),
('Volunteer Biologist', 'Biologist')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- ATOMIC LOGIC: vault_finalize_intake RPC
-- =============================================================================

CREATE OR REPLACE FUNCTION public.vault_finalize_intake(p_payload jsonb)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_species_id text;
  v_next_intake int;
  v_intake_date date;
  v_session_id text;
  v_observer_id uuid;
  v_mother_id text;
  v_bin jsonb;
  v_bin_id text;
  v_notes text;
  v_egg_count int;
  v_first_bin text := NULL;
BEGIN
  -- 1. Extract and Validate Header Logic
  v_species_id := p_payload->>'species_id';
  v_next_intake := (p_payload->>'next_intake_number')::int;
  v_intake_date := (p_payload->>'intake_date')::date;
  v_session_id := p_payload->>'session_id';
  v_observer_id := (p_payload->>'observer_id')::uuid;

  IF v_species_id IS NULL OR v_next_intake IS NULL OR v_session_id IS NULL OR v_observer_id IS NULL THEN
    RAISE EXCEPTION 'vault_finalize_intake: missing required payload fields';
  END IF;

  -- 2. Update Global Species Counter
  UPDATE public.species SET intake_count = v_next_intake WHERE species_id = v_species_id;

  -- 3. Create Maternal Case Record
  v_mother_id := 'M' || to_char(clock_timestamp(), 'YYYYMMDDHH24MISS');
  
  INSERT INTO public.mother (
    mother_id,
    mother_name,
    finder_turtle_name,
    species_id,
    intake_date,
    intake_condition,
    extraction_method,
    discovery_location,
    carapace_length_mm,
    session_id,
    created_by_id,
    modified_by_id
  ) VALUES (
    v_mother_id,
    NULLIF(p_payload#>>'{mother,mother_name}', ''),
    NULLIF(p_payload#>>'{mother,finder_turtle_name}', ''),
    v_species_id,
    COALESCE(NULLIF(p_payload#>>'{mother,intake_date}', '')::date, v_intake_date),
    NULLIF(p_payload#>>'{mother,intake_condition}', ''),
    NULLIF(p_payload#>>'{mother,extraction_method}', ''),
    NULLIF(p_payload#>>'{mother,discovery_location}', ''),
    NULLIF(p_payload#>>'{mother,carapace_length_mm}', '')::numeric,
    v_session_id,
    v_observer_id,
    v_observer_id
  );

  -- 4. Process Bin & Egg Batches
  FOR v_bin IN SELECT * FROM jsonb_array_elements(p_payload->'bins')
  LOOP
    v_bin_id := v_bin->>'bin_id';
    v_notes := COALESCE(v_bin->>'bin_notes', 'Clinical Intake Baseline');
    v_egg_count := COALESCE((v_bin->>'egg_count')::int, 0);

    IF v_first_bin IS NULL THEN v_first_bin := v_bin_id; END IF;

    -- Create Bin
    INSERT INTO public.bin (
      bin_id, mother_id, bin_notes, session_id, created_by_id, modified_by_id
    ) VALUES (
      v_bin_id, v_mother_id, v_notes, v_session_id, v_observer_id, v_observer_id
    );

    -- Create Eggs & Baseline Observations
    FOR i IN 1..v_egg_count LOOP
      DECLARE
        v_egg_id text;
      BEGIN
        v_egg_id := v_bin_id || '-E' || i;
        
        INSERT INTO public.egg (
          egg_id, bin_id, status, current_stage, intake_date, 
          session_id, created_by_id, modified_by_id
        ) VALUES (
          v_egg_id, v_bin_id, 'Active', 'S0', v_intake_date,
          v_session_id, v_observer_id, v_observer_id
        );

        INSERT INTO public.egg_observation (
          session_id, egg_id, bin_id, observer_id, stage_at_observation, notes, created_by_id, modified_by_id
        ) VALUES (
          v_session_id, v_egg_id, v_bin_id, v_observer_id, 'S0', 'Intake Baseline', v_observer_id, v_observer_id
        );
      END;
    END LOOP;
  END LOOP;

  -- 5. Return Handshake
  RETURN jsonb_build_object(
    'mother_id', v_mother_id,
    'first_bin_id', v_first_bin
  );
END;
$$;

GRANT EXECUTE ON FUNCTION public.vault_finalize_intake(jsonb) TO service_role;

COMMIT;
