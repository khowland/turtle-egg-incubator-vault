-- =============================================================================
-- Migration: 20260408_v7_2_0_DEEP_DIVE.sql (MASTER CONSOLIDATED - v4 ROBUST)
-- Project:   Incubator Vault v7.2.0 — Wildlife In Need Center (WINC)
-- Purpose:   Robust One-File Deployment that handles multiple UNIQUE 
--            constaint conflicts and includes the new intake_count tracker.
-- =============================================================================

-- 1. INFRASTRUCTURE: Global Audit & Modification Support
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. BIOLOGICAL REGISTRY: Full Wisconsin Registry (§3.2 / §8 / 2002)
ALTER TABLE species ADD COLUMN IF NOT EXISTS species_code CHAR(2);
ALTER TABLE species ADD COLUMN IF NOT EXISTS intake_count INTEGER DEFAULT 0;

DO $$
DECLARE
    s RECORD;
BEGIN
    FOR s IN SELECT * FROM (VALUES 
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
    ) AS t(id, common, scientific, code, status)
    LOOP
        UPDATE species 
        SET species_code = s.code, 
            scientific_name = s.scientific,
            vulnerability_status = s.status,
            intake_count = COALESCE(intake_count, 0)
        WHERE species_id = s.id 
           OR common_name = s.common 
           OR scientific_name = s.scientific;

        IF NOT FOUND THEN
            INSERT INTO species (species_id, common_name, scientific_name, species_code, vulnerability_status, intake_count)
            VALUES (s.id, s.common, s.scientific, s.code, s.status, 0);
        END IF;
    END LOOP;
END $$;

-- 3. LOOKUP ENTITIES: Stages & Properties (§4.42)
CREATE TABLE IF NOT EXISTS development_stage (
    stage_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS biological_property (
    property_id TEXT PRIMARY KEY,
    stage_id TEXT REFERENCES development_stage(stage_id),
    property_label TEXT NOT NULL,
    data_type TEXT DEFAULT 'BOOLEAN', 
    is_critical BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO development_stage (stage_id, label) VALUES 
('S0', 'Intake'), ('S1', 'Warming'), ('S2', 'Development'), 
('S3', 'Established'), ('S4', 'Mature'), ('S5', 'Pipping'), ('S6', 'Hatched')
ON CONFLICT (stage_id) DO NOTHING;

-- 4. HATCHLING LEDGER: Neonate Pivot (§3.4)
CREATE TABLE IF NOT EXISTS hatchling_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id TEXT NOT NULL,
    mother_id TEXT NOT NULL,
    session_id TEXT,
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g DECIMAL(10,2),
    incubation_duration_days INTEGER,
    vitality_score TEXT, 
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 5. HYDRATION ENGINE: Restorative Logic (§3.2 / §2.18)
ALTER TABLE bin ADD COLUMN IF NOT EXISTS target_total_weight_g DECIMAL(10,2);
ALTER TABLE bin ADD COLUMN IF NOT EXISTS shelf_location TEXT;
ALTER TABLE bin ADD COLUMN IF NOT EXISTS substrate TEXT;
ALTER TABLE bin ADD COLUMN IF NOT EXISTS total_water_added_season_ml DECIMAL(10,2) DEFAULT 0.0;
ALTER TABLE bin ADD COLUMN IF NOT EXISTS last_moisture_deficit_g DECIMAL(10,2);

-- Standardizing Observation Tables
DO $$ BEGIN
    ALTER TABLE "IncubatorObservation" ADD COLUMN IF NOT EXISTS bin_weight_g DECIMAL(10,2);
    ALTER TABLE "IncubatorObservation" ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);
    ALTER TABLE "EggObservation" ADD COLUMN IF NOT EXISTS moisture_deficit_g DECIMAL(10,2);
    ALTER TABLE "EggObservation" ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);
EXCEPTION WHEN others THEN RAISE NOTICE 'Observation table column update skipped - verify table casing';
END $$;

-- 6. AUDIT LAYER: Mandatory Fields (§6.53)
DO $$ 
BEGIN
    ALTER TABLE mother ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE mother ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE egg ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    ALTER TABLE egg ADD COLUMN IF NOT EXISTS modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
END $$;

-- 7. AUTOMATION: Global Audit Triggers
DO $$
DECLARE
    t text;
BEGIN
    FOR t IN SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%I_modtime ON %I', t, t);
        EXECUTE format('CREATE TRIGGER update_%I_modtime BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_modified_column()', t, t);
    END LOOP;
END $$;
