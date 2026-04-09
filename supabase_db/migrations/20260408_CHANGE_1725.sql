-- =============================================================================
-- Migration: 20260408_CHANGE_1725.sql
-- Project:   Incubator Vault v7.2.0 — WINC
-- Purpose:   Implementing Finder Name, 11-Species Registry, and 
--            UI nomenclature simplification.
-- =============================================================================

-- 1. Maternal Record Update (§3.1)
ALTER TABLE mother ADD COLUMN IF NOT EXISTS finder_turtle_name TEXT;

-- 2. Species Registry Integrity Check (Full 11 native species)
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
ON CONFLICT (common_name) DO UPDATE SET 
    species_code = EXCLUDED.species_code,
    scientific_name = EXCLUDED.scientific_name;

-- 3. Trigger Refresh
-- Ensure the new finder name is available in mother_id generation if needed
CREATE OR REPLACE FUNCTION generate_mother_id_v72()
RETURNS TRIGGER AS $$
BEGIN
    NEW.mother_id := COALESCE(NEW.finder_last_name, 'Unknown') || '-' || 
                     NEW.mother_name || '-' || 
                     TO_CHAR(NEW.intake_date, 'YYYYMMDD');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
