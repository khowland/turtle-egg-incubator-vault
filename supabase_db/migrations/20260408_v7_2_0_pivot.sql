-- =============================================================================
-- Migration: 20260408_v7_2_0_pivot.sql
-- Project:   Incubator Vault v7.2.0 — Wildlife In Need Center (WINC)
-- Purpose:   Standardized Species Registry (11 Native WI Species), 
--            Hatchling_Ledger, and Restorative Hydration Logic.
-- =============================================================================

-- 1. Full Wisconsin Biological Registry (§3.2 / §8)
ALTER TABLE species ADD COLUMN IF NOT EXISTS species_code CHAR(2) UNIQUE;

INSERT INTO species (species_id, common_name, scientific_name, species_code, vulnerability_status)
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
ON CONFLICT (species_id) DO UPDATE SET 
    species_code = EXCLUDED.species_code,
    scientific_name = EXCLUDED.scientific_name,
    vulnerability_status = EXCLUDED.vulnerability_status;

-- 2. Create Hatchling_Ledger Table (§3.4)
CREATE TABLE IF NOT EXISTS hatchling_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id TEXT, -- Legacy egg IDs are text strings
    mother_id TEXT,
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g DECIMAL(10,2),
    vitality_score TEXT, 
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 3. Update Bin Table for Restorative Hydration (§3.2)
ALTER TABLE bin ADD COLUMN IF NOT EXISTS target_total_weight_g DECIMAL(10,2);
ALTER TABLE bin ADD COLUMN IF NOT EXISTS shelf_location TEXT;
ALTER TABLE bin ADD COLUMN IF NOT EXISTS substrate TEXT;

-- 4. Update EggObservation for Weight Tracking
-- Using lowercase to match Postgres standard as requested in previous sessions
ALTER TABLE "EggObservation" ADD COLUMN IF NOT EXISTS bin_weight_at_obs_g DECIMAL(10,2);
ALTER TABLE "EggObservation" ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);
ALTER TABLE "EggObservation" ADD COLUMN IF NOT EXISTS moisture_deficit_g DECIMAL(10,2);

-- 5. Atomic ID Generation Update (v7.2.0 Nomenclature)
CREATE OR REPLACE FUNCTION generate_bin_id_v2()
RETURNS TRIGGER AS $$
DECLARE
    s_code CHAR(2);
    next_bin_num INTEGER;
BEGIN
    SELECT s.species_code INTO s_code 
    FROM species s 
    JOIN mother m ON m.species_id = s.species_id 
    WHERE m.mother_id = NEW.mother_id;
    
    SELECT COALESCE(COUNT(*), 0) + 1 INTO next_bin_num FROM bin WHERE mother_id = NEW.mother_id;
    
    IF NEW.bin_id IS NULL THEN
        NEW.bin_id := NEW.mother_id || '-' || COALESCE(s_code, 'UN') || '-B' || next_bin_num;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
