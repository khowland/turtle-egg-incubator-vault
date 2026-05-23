CREATE OR REPLACE FUNCTION public.reset_species_to_defaults()
RETURNS void AS $$
BEGIN
    -- Purge current entries
    TRUNCATE TABLE public.species CASCADE;

    -- Re-insert the master Wisconsin dataset
    INSERT INTO public.species 
    (species_id, common_name, scientific_name, incubation_min_days, incubation_max_days, optimal_temp_low, optimal_temp_high, vulnerability_status, species_code, family, is_subspecies, min_clutch_size, max_clutch_size, avg_egg_weight_grams, shell_type)
    VALUES 
    ('SN-SER', 'Common Snapping Turtle', 'Chelydra serpentina', 60, 90, 25.0, 30.0, 'Common', 'SN', 'Chelydridae', false, 20, 80, 15.00, 'Flexible'),
    ('PT-MAR', 'Midland Painted Turtle', 'Chrysemys picta marginata', 60, 80, 25.0, 30.0, 'Common', 'PM', 'Emydidae', true, 5, 15, 7.00, 'Flexible'),
    ('PT-BEL', 'Western Painted Turtle', 'Chrysemys picta bellii', 60, 80, 25.0, 30.0, 'Common', 'PW', 'Emydidae', true, 5, 15, 7.00, 'Flexible'),
    ('BL-BLA', 'Blanding''s Turtle', 'Emydoidea blandingii', 60, 90, 26.5, 30.0, 'Special Concern', 'BL', 'Emydidae', false, 6, 15, 12.50, 'Flexible'),
    ('WD-INS', 'Wood Turtle', 'Glyptemys insculpta', 60, 75, 25.0, 29.0, 'Threatened', 'WD', 'Emydidae', false, 5, 12, 12.50, 'Flexible'),
    ('NM-GEO', 'Northern Map Turtle', 'Graptemys geographica', 60, 85, 25.0, 30.0, 'Common', 'NM', 'Emydidae', false, 8, 16, 12.50, 'Flexible'),
    ('OM-OUA', 'Ouachita Map Turtle', 'Graptemys ouachitensis ouachitensis', 60, 85, 25.0, 30.0, 'Common', 'OM', 'Emydidae', true, 8, 15, 10.00, 'Flexible'),
    ('FM-PSE', 'False Map Turtle', 'Graptemys pseudogeographica pseudogeographica', 60, 85, 25.0, 30.0, 'Common', 'FM', 'Emydidae', true, 10, 20, 10.00, 'Flexible'),
    ('OB-ORN', 'Ornate Box Turtle', 'Terrapene ornata ornata', 50, 70, 26.0, 30.0, 'Endangered', 'OB', 'Emydidae', true, 2, 8, 10.00, 'Flexible'),
    ('MU-ODO', 'Eastern Musk Turtle', 'Sternotherus odoratus', 60, 100, 24.0, 29.0, 'Common', 'MU', 'Kinosternidae', false, 1, 9, 5.50, 'Brittle'),
    ('SS-MUT', 'Midland Smooth Softshell', 'Apalone mutica mutica', 60, 90, 25.0, 30.0, 'Special Concern', 'SM', 'Trionychidae', true, 5, 20, 4.50, 'Brittle'),
    ('SS-SPI', 'Eastern Spiny Softshell', 'Apalone spinifera spinifera', 60, 90, 25.0, 30.0, 'Common', 'SS', 'Trionychidae', true, 9, 30, 6.00, 'Brittle');
END;
$$ LANGUAGE plpgsql;