BEGIN;
-- 1. Rename 'mother' to 'intake'
ALTER TABLE IF EXISTS public.mother RENAME TO intake;
ALTER TABLE IF EXISTS public.intake RENAME COLUMN mother_id TO intake_id;
ALTER TABLE IF EXISTS public.intake RENAME COLUMN mother_name TO intake_name;

ALTER TABLE IF EXISTS public.bin RENAME COLUMN mother_id TO intake_id;
ALTER TABLE IF EXISTS public.hatchling_ledger RENAME COLUMN mother_id TO intake_id;

-- 2. Date Standardization
ALTER TABLE IF EXISTS public.bin RENAME COLUMN bin_date TO bin_date;

DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bin_observation' AND column_name = 'egg_observation_date') THEN
        ALTER TABLE public.bin_observation RENAME COLUMN egg_observation_date TO bin_observation_date;
    END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'egg_observation' AND column_name = 'egg_observation_date') THEN
        ALTER TABLE public.egg_observation RENAME COLUMN egg_observation_date TO egg_observation_date;
    END IF;
END $$;

-- 3. S0 Purge: Baseline all intake records at S1
UPDATE public.egg SET current_stage = 'S1' WHERE current_stage = 'S0';
UPDATE public.egg_observation SET stage_at_observation = 'S1' WHERE stage_at_observation = 'S0';
DELETE FROM public.development_stage WHERE stage_id = 'S0';

-- 4. 12-stage lookup re-seed
INSERT INTO public.development_stage (stage_id, milestone, sub_code, label, ordinal_rank, description) VALUES
('S1',     'S1', NULL,  'Intake',  100, 'Baseline post-oviposition entry.'),
('S2S',    'S2', 'S',   'Spot',    200, 'Initial chalking spot at apex.'),
('S2B',    'S2', 'B',   'Band',    210, 'Equatorial calcification band.'),
('S2F',    'S2', 'F',   'Full',    220, 'Total calcification (Joint-Covering).'),
('S3',     'S3', NULL,  'Veins',   300, 'Vascularization: Vitelline veins visible.'),
('S4C',    'S4', 'C',   'C-Stage', 400, 'Early embryonic curve (Shrimp).'),
('S4T',    'S4', 'T',   'Term',    410, 'Advanced development shadow occlusion.'),
('S4M',    'S4', 'M',   'Motion',  420, 'Somatic movement detected.'),
('S5',     'S5', NULL,  'Pipping', 500, 'Mechanical shell breach initiated.'),
('S6-YA1', 'S6', 'YA1', 'Hatch 1', 600, 'Hatched; Full Yolk Sac external.'),
('S6-YA2', 'S6', 'YA2', 'Hatch 2', 610, 'Hatched; Half Yolk absorbed.'),
('S6-YA3', 'S6', 'YA3', 'Hatch 3', 620, 'Hatched; Fully Absorbed (READY TO EXPORT).')
ON CONFLICT (stage_id) DO UPDATE SET 
    milestone = EXCLUDED.milestone, sub_code = EXCLUDED.sub_code, 
    label = EXCLUDED.label, ordinal_rank = EXCLUDED.ordinal_rank, description = EXCLUDED.description;

-- 5. system_config biosecurity gates
INSERT INTO public.system_config (config_key, config_value, description)
VALUES ('MIN_EXPORT_STAGE_ORDINAL', '620', 'Minimum developmental stage (ordinal) required for site export.')
ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value, description = EXCLUDED.description;

COMMIT;
