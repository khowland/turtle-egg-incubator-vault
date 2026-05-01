-- CR-20260430-194500: Seed lookup tables with default species, development stages, and biological properties

-- ============================================================
-- SPECIES (Wisconsin native turtle species)
-- ============================================================
INSERT INTO public.species (species_id, species_code, common_name, scientific_name, intake_count, created_at, modified_at)
VALUES
    ('BL', 'BL', 'Blanding''s Turtle', 'Emydoidea blandingii', 0, NOW(), NOW()),
    ('MK', 'MK', 'Common Musk Turtle (Stinkpot)', 'Sternotherus odoratus', 0, NOW(), NOW()),
    ('PT', 'PT', 'Painted Turtle', 'Chrysemys picta', 0, NOW(), NOW()),
    ('SN', 'SN', 'Common Snapping Turtle', 'Chelydra serpentina', 0, NOW(), NOW()),
    ('SP', 'SP', 'Spiny Softshell Turtle', 'Apalone spinifera', 0, NOW(), NOW()),
    ('MT', 'MT', 'Map Turtle', 'Graptemys geographica', 0, NOW(), NOW()),
    ('WD', 'WD', 'Wood Turtle', 'Glyptemys insculpta', 0, NOW(), NOW()),
    ('BX', 'BX', 'Eastern Box Turtle', 'Terrapene carolina', 0, NOW(), NOW())
ON CONFLICT (species_id) DO NOTHING;

-- ============================================================
-- DEVELOPMENT STAGES (S0-S6 with sub-stages)
-- ============================================================
-- First ensure the table has a 'sub_code' column
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'development_stage' AND column_name = 'sub_code'
    ) THEN
        ALTER TABLE public.development_stage ADD COLUMN sub_code text;
    END IF;
END $$;

INSERT INTO public.development_stage (stage_id, label, description, milestone, ordinal_rank, sub_code, created_at, modified_at)
VALUES
    ('S0', 'Pre-Intake', 'Egg received but not yet assessed or classified', NULL, 0, NULL, NOW(), NOW()),
    ('S1', 'Intake', 'Initial intake baseline established with measurements', NULL, 1, NULL, NOW(), NOW()),
    ('S2-Spot', 'Early Development — Spot', 'Round opaque spot visible on yolk — early embryo', NULL, 2, 'Spot', NOW(), NOW()),
    ('S2-Band', 'Early Development — Band', 'Embryonic band visible across egg circumference', NULL, 2, 'Band', NOW(), NOW()),
    ('S2-Full', 'Early Development — Full', 'Full embryo disc visible in early organogenesis', NULL, 2, 'Full', NOW(), NOW()),
    ('S3', 'Mid Development', 'Embryo body shape visible; limb buds forming', NULL, 3, NULL, NOW(), NOW()),
    ('S4-C', 'Late Development — C Stage', 'Carapace scutes visible; pigmentation beginning', NULL, 4, 'C', NOW(), NOW()),
    ('S4-Term', 'Late Development — Terminal', 'Full term embryo; yolk sac external but reducing', NULL, 4, 'Term', NOW(), NOW()),
    ('S4-Motion', 'Late Development — Motion', 'Embryo moving inside egg; imminent hatch expected', NULL, 4, 'Motion', NOW(), NOW()),
    ('S5', 'Hatching', 'Pipping or actively emerging from shell', NULL, 5, NULL, NOW(), NOW()),
    ('S6-YA1', 'Hatchling — Yearling Age 1', 'Post-hatch; external yolk sac absorbed; umbilical healed', NULL, 6, 'YA1', NOW(), NOW()),
    ('S6-YA2', 'Hatchling — Yearling Age 2', '6-12 months; feeding independently; rapid growth phase', NULL, 6, 'YA2', NOW(), NOW()),
    ('S6-YA3', 'Hatchling — Yearling Age 3', '12+ months; ready for release or transfer; biosecurity gate for WormD export', NULL, 6, 'YA3', NOW(), NOW()),
    ('SX', 'Non-Viable', 'Egg failed to develop; determined non-viable', NULL, 99, NULL, NOW(), NOW()),
    ('SD', 'Deceased', 'Embryo or hatchling died', NULL, 98, NULL, NOW(), NOW())
ON CONFLICT (stage_id) DO NOTHING;

-- ============================================================
-- BIOLOGICAL PROPERTIES (observation metrics per stage)
-- ============================================================
INSERT INTO public.biological_property (property_id, stage_id, property_label, data_type, is_critical, created_at, modified_at)
VALUES
    -- S1 (Intake) properties
    ('s1_mass', 'S1', 'Egg Mass (g)', 'NUMERIC', true, NOW(), NOW()),
    ('s1_diameter', 'S1', 'Egg Diameter (mm)', 'NUMERIC', true, NOW(), NOW()),
    ('s1_condition', 'S1', 'Egg Condition', 'TEXT', true, NOW(), NOW()),
    
    -- S2 properties
    ('s2_molding', 'S2-Spot', 'Molding (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_chalking', 'S2-Spot', 'Chalking (0-2)', 'INTEGER_0_2', true, NOW(), NOW()),
    ('s2_vascularity', 'S2-Spot', 'Vascularity Present', 'BOOLEAN', true, NOW(), NOW()),
    ('s2_dented', 'S2-Spot', 'Dented (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_discolored', 'S2-Spot', 'Discolored', 'BOOLEAN', false, NOW(), NOW()),
    ('s2_molding_band', 'S2-Band', 'Molding (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_chalking_band', 'S2-Band', 'Chalking (0-2)', 'INTEGER_0_2', true, NOW(), NOW()),
    ('s2_vascularity_band', 'S2-Band', 'Vascularity Present', 'BOOLEAN', true, NOW(), NOW()),
    ('s2_dented_band', 'S2-Band', 'Dented (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_discolored_band', 'S2-Band', 'Discolored', 'BOOLEAN', false, NOW(), NOW()),
    ('s2_molding_full', 'S2-Full', 'Molding (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_chalking_full', 'S2-Full', 'Chalking (0-2)', 'INTEGER_0_2', true, NOW(), NOW()),
    ('s2_vascularity_full', 'S2-Full', 'Vascularity Present', 'BOOLEAN', true, NOW(), NOW()),
    ('s2_dented_full', 'S2-Full', 'Dented (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_discolored_full', 'S2-Full', 'Discolored', 'BOOLEAN', false, NOW(), NOW()),
    
    -- S3 properties
    ('s3_molding', 'S3', 'Molding (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s3_chalking', 'S3', 'Chalking (0-2)', 'INTEGER_0_2', true, NOW(), NOW()),
    ('s3_vascularity', 'S3', 'Vascularity Present', 'BOOLEAN', true, NOW(), NOW()),
    ('s3_leaking', 'S3', 'Leaking (0-4)', 'INTEGER_0_4', true, NOW(), NOW()),
    ('s3_dented', 'S3', 'Dented (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s3_discolored', 'S3', 'Discolored', 'BOOLEAN', false, NOW(), NOW()),
    ('s3_moisture_deficit', 'S3', 'Moisture Deficit', 'NUMERIC', false, NOW(), NOW()),
    ('s3_water_added', 'S3', 'Water Added (mL)', 'NUMERIC', false, NOW(), NOW()),
    
    -- S4 properties
    ('s4_molding', 'S4-C', 'Molding (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s4_chalking', 'S4-C', 'Chalking (0-2)', 'INTEGER_0_2', true, NOW(), NOW()),
    ('s4_vascularity', 'S4-C', 'Vascularity Present', 'BOOLEAN', true, NOW(), NOW()),
    ('s4_leaking', 'S4-C', 'Leaking (0-4)', 'INTEGER_0_4', true, NOW(), NOW()),
    ('s4_dented', 'S4-C', 'Dented (0-4)', 'INTEGER_0_4', false, NOW(), NOW()),
    ('s4_discolored', 'S4-C', 'Discolored', 'BOOLEAN', false, NOW(), NOW()),
    ('s4_moisture_deficit', 'S4-C', 'Moisture Deficit', 'NUMERIC', false, NOW(), NOW()),
    ('s4_water_added', 'S4-C', 'Water Added (mL)', 'NUMERIC', false, NOW(), NOW()),
    ('s4_motion', 'S4-Motion', 'Motion Observed', 'BOOLEAN', true, NOW(), NOW()),
    ('s4_pipping', 'S4-Motion', 'Pipping Observed', 'BOOLEAN', true, NOW(), NOW()),
    
    -- S5 properties
    ('s5_emerging', 'S5', 'Actively Emerging', 'BOOLEAN', true, NOW(), NOW()),
    ('s5_yolk_sac', 'S5', 'External Yolk Sac Present', 'BOOLEAN', true, NOW(), NOW()),
    
    -- S6 properties
    ('s6_weight', 'S6-YA1', 'Weight (g)', 'NUMERIC', true, NOW(), NOW()),
    ('s6_umbilical', 'S6-YA1', 'Umbilical Healed', 'BOOLEAN', true, NOW(), NOW()),
    ('s6_feeding', 'S6-YA1', 'Feeding Independently', 'BOOLEAN', true, NOW(), NOW())
ON CONFLICT (property_id) DO NOTHING;
