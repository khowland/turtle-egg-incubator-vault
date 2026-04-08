-- =============================================================================
-- Migration: 20260408_v7_2_0_DEEP_DIVE.sql
-- Project:   Incubator Vault v7.2.0 — Wildlife In Need Center (WINC)
-- Purpose:   Global Refactoring for v7.2.0 Compliance (Audit, Locks, & Metrics)
-- =============================================================================

-- 1. Infrastructure: Global Audit & Modification Support
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Biological Lookups (§4.42): Stages & Properties
CREATE TABLE IF NOT EXISTS development_stage (
    stage_id TEXT PRIMARY KEY, -- S0, S1, S2, etc.
    label TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS biological_property (
    property_id TEXT PRIMARY KEY,
    stage_id TEXT REFERENCES development_stage(stage_id),
    property_label TEXT NOT NULL,
    data_type TEXT DEFAULT 'BOOLEAN', -- BOOLEAN, SCALE_0_2, TEXT
    is_critical BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed Stages
INSERT INTO development_stage (stage_id, label) VALUES 
('S0', 'Intake'), ('S1', 'Warming'), ('S2', 'Development'), 
('S3', 'Established'), ('S4', 'Mature'), ('S5', 'Pipping'), ('S6', 'Hatched')
ON CONFLICT (stage_id) DO NOTHING;

-- 3. Standardized Audit Columns for Existing Tables (§53)
DO $$ 
BEGIN
    -- Add to species
    ALTER TABLE species ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE species ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    -- Add to mother
    ALTER TABLE mother ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE mother ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    -- Add to bin
    ALTER TABLE bin ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE bin ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    -- Add to egg
    ALTER TABLE egg ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE egg ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
END $$;

-- 4. Expanded Hatchling_Ledger (§3.4)
CREATE TABLE IF NOT EXISTS hatchling_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id TEXT NOT NULL,
    mother_id TEXT NOT NULL,
    session_id TEXT, -- Link to the session that performed the pivot
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g DECIMAL(10,2),
    incubation_duration_days INTEGER,
    vitality_score TEXT, 
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 5. Restorative Hydration Extensions (§2.18)
-- Adding historical tracking to the bin for the Hydration Correlation Report
ALTER TABLE bin ADD COLUMN IF NOT EXISTS total_water_added_season_ml DECIMAL(10,2) DEFAULT 0.0;
ALTER TABLE bin ADD COLUMN IF NOT EXISTS last_moisture_deficit_g DECIMAL(10,2);
ALTER TABLE bin ADD COLUMN IF NOT EXISTS last_hydration_timestamp TIMESTAMP WITH TIME ZONE;

-- 6. Environment Observation Refactoring
-- Deprecating sensors, prioritizing weight in the Env table
ALTER TABLE "IncubatorObservation" ADD COLUMN IF NOT EXISTS bin_weight_g DECIMAL(10,2);
ALTER TABLE "IncubatorObservation" ADD COLUMN IF NOT EXISTS moisture_deficit_g DECIMAL(10,2);
ALTER TABLE "IncubatorObservation" ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);

-- 7. Apply Update Triggers to ALL Tables
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%I_modtime ON %I', t, t);
        EXECUTE format('CREATE TRIGGER update_%I_modtime BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_modified_column()', t, t);
    END LOOP;
END $$;
