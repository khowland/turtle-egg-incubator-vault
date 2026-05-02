-- ============================================================================
-- CR-20260501-1800: Numeric PK/FK Migration v9.1.0
-- Purpose: Convert bin.bin_id and development_stage.stage_id from text to BIGINT
--          Update all foreign key references accordingly
-- ============================================================================

BEGIN;

-- ============================================================================
-- PHASE A: TRUNCATE ALL TRANSACTION TABLES
-- Keep lookup tables: species, observer, system_config (truncate everything else)
-- ============================================================================
TRUNCATE TABLE public.hatchling_ledger CASCADE;
TRUNCATE TABLE public.egg_observation CASCADE;
TRUNCATE TABLE public.bin_observation CASCADE;
TRUNCATE TABLE public.egg CASCADE;
TRUNCATE TABLE public.bin CASCADE;
TRUNCATE TABLE public.intake CASCADE;
TRUNCATE TABLE public.session_log CASCADE;
TRUNCATE TABLE public.system_log CASCADE;

-- ============================================================================
-- PHASE B: DROP FK CONSTRAINTS REFERENCING bin.bin_id
-- ============================================================================
ALTER TABLE public.bin_observation DROP CONSTRAINT IF EXISTS incubatorobservation_bin_id_fkey;
ALTER TABLE public.egg DROP CONSTRAINT IF EXISTS egg_bin_id_fkey;
ALTER TABLE public.egg_observation DROP CONSTRAINT IF EXISTS egg_observation_bin_id_fkey;

-- ============================================================================
-- PHASE C: CONVERT bin.bin_id FROM text TO BIGINT
-- ============================================================================

-- C.1: Drop primary key constraint (CASCADE also drops remaining FK refs from other tables)
ALTER TABLE public.bin DROP CONSTRAINT IF EXISTS bin_pkey CASCADE;

-- C.2: Add new BIGINT IDENTITY column
ALTER TABLE public.bin ADD COLUMN bin_id_new BIGINT GENERATED ALWAYS AS IDENTITY;

-- C.3: Drop old text column
ALTER TABLE public.bin DROP COLUMN IF EXISTS bin_id;

-- C.4: Rename new column to bin_id
ALTER TABLE public.bin RENAME COLUMN bin_id_new TO bin_id;

-- C.5: Add primary key constraint on new column
ALTER TABLE public.bin ADD CONSTRAINT bin_pkey PRIMARY KEY (bin_id);

-- ============================================================================
-- PHASE D: CONVERT FK COLUMNS IN CHILD TABLES TO BIGINT
-- ============================================================================
ALTER TABLE public.egg ADD COLUMN bin_id_new BIGINT;
ALTER TABLE public.bin_observation ADD COLUMN bin_id_new BIGINT;
ALTER TABLE public.egg_observation ADD COLUMN bin_id_new BIGINT;

-- ============================================================================
-- PHASE E: DROP OLD FK COLUMNS AND RENAME NEW ONES
-- ============================================================================
ALTER TABLE public.egg DROP COLUMN IF EXISTS bin_id;
ALTER TABLE public.egg RENAME COLUMN bin_id_new TO bin_id;

ALTER TABLE public.bin_observation DROP COLUMN IF EXISTS bin_id;
ALTER TABLE public.bin_observation RENAME COLUMN bin_id_new TO bin_id;

ALTER TABLE public.egg_observation DROP COLUMN IF EXISTS bin_id;
ALTER TABLE public.egg_observation RENAME COLUMN bin_id_new TO bin_id;

-- ============================================================================
-- PHASE F: RE-ADD FK CONSTRAINTS TO CHILD TABLES
-- ============================================================================
ALTER TABLE public.egg 
    ADD CONSTRAINT egg_bin_id_fkey 
    FOREIGN KEY (bin_id) REFERENCES public.bin(bin_id);

ALTER TABLE public.bin_observation 
    ADD CONSTRAINT bin_observation_bin_id_fkey 
    FOREIGN KEY (bin_id) REFERENCES public.bin(bin_id);

ALTER TABLE public.egg_observation 
    ADD CONSTRAINT egg_observation_bin_id_fkey 
    FOREIGN KEY (bin_id) REFERENCES public.bin(bin_id);

-- ============================================================================
-- PHASE G: CONVERT development_stage.stage_id FROM text TO BIGINT
-- ============================================================================

-- G.1: Drop FK constraint referencing development_stage.stage_id
-- Note: egg.current_stage is text with NO foreign key constraint to development_stage
ALTER TABLE public.biological_property DROP CONSTRAINT IF EXISTS biological_property_stage_id_fkey;

-- G.2: Drop primary key constraint (CASCADE drops any remaining FK refs)
ALTER TABLE public.development_stage DROP CONSTRAINT IF EXISTS development_stage_pkey CASCADE;

-- G.3: Add new BIGINT IDENTITY column
ALTER TABLE public.development_stage ADD COLUMN stage_id_new BIGINT GENERATED ALWAYS AS IDENTITY;

-- G.4: Drop old text column
ALTER TABLE public.development_stage DROP COLUMN IF EXISTS stage_id;

-- G.5: Rename new column
ALTER TABLE public.development_stage RENAME COLUMN stage_id_new TO stage_id;

-- G.6: Add primary key constraint
ALTER TABLE public.development_stage ADD CONSTRAINT development_stage_pkey PRIMARY KEY (stage_id);

-- G.7: Convert biological_property FK column
ALTER TABLE public.biological_property ADD COLUMN stage_id_new BIGINT;
ALTER TABLE public.biological_property DROP COLUMN IF EXISTS stage_id;
ALTER TABLE public.biological_property RENAME COLUMN stage_id_new TO stage_id;

-- G.8: Re-add FK constraint on biological_property
ALTER TABLE public.biological_property 
    ADD CONSTRAINT biological_property_stage_id_fkey 
    FOREIGN KEY (stage_id) REFERENCES public.development_stage(stage_id);

-- ============================================================================
-- PHASE H: RE-SEED LOOKUP TABLES
-- development_stage and biological_property need truncation before re-seeding
-- since text stage_ids are gone and new BIGINT IDs need clean slate
-- ============================================================================

TRUNCATE TABLE public.biological_property CASCADE;
TRUNCATE TABLE public.development_stage CASCADE;

-- H.1: Re-seed development_stage with explicit numeric IDs using OVERRIDING SYSTEM VALUE
-- (GENERATED ALWAYS AS IDENTITY requires OVERRIDING SYSTEM VALUE for explicit inserts)
INSERT INTO public.development_stage (stage_id, label, description, ordinal_rank, egg_stage_code, created_at, modified_at)
OVERRIDING SYSTEM VALUE
VALUES
    (1,  'Pre-Intake',                     'Egg received but not yet assessed or classified',         0,  NULL,        NOW(), NOW()),
    (2,  'Intake',                         'Initial intake baseline established with measurements',    1,  NULL,        NOW(), NOW()),
    (3,  'Early Development — Spot',       'Round opaque spot visible on yolk — early embryo',         2,  'Spot',      NOW(), NOW()),
    (4,  'Early Development — Band',       'Embryonic band visible across egg circumference',          2,  'Band',      NOW(), NOW()),
    (5,  'Early Development — Full',       'Full embryo disc visible in early organogenesis',          2,  'Full',      NOW(), NOW()),
    (6,  'Mid Development',                'Embryo body shape visible; limb buds forming',             3,  NULL,        NOW(), NOW()),
    (7,  'Late Development — C Stage',     'Carapace scutes visible; pigmentation beginning',          4,  'C',         NOW(), NOW()),
    (8,  'Late Development — Terminal',    'Full term embryo; yolk sac external but reducing',         4,  'Term',      NOW(), NOW()),
    (9,  'Late Development — Motion',      'Embryo moving inside egg; imminent hatch expected',        4,  'Motion',    NOW(), NOW()),
    (10, 'Hatching',                       'Pipping or actively emerging from shell',                  5,  NULL,        NOW(), NOW()),
    (11, 'Hatchling — Yearling Age 1',     'Post-hatch; external yolk sac absorbed; umbilical healed', 6,  'YA1',       NOW(), NOW()),
    (12, 'Hatchling — Yearling Age 2',     '6-12 months; feeding independently; rapid growth phase',   6,  'YA2',       NOW(), NOW()),
    (13, 'Hatchling — Yearling Age 3',     '12+ months; ready for release or transfer',                6,  'YA3',       NOW(), NOW()),
    (14, 'Non-Viable',                     'Egg failed to develop; determined non-viable',             99, NULL,        NOW(), NOW()),
    (15, 'Deceased',                       'Embryo or hatchling died',                                 98, NULL,        NOW(), NOW());

-- H.1b: Reset IDENTITY sequence so next auto-generated stage_id starts after our manual IDs
SELECT setval(
    pg_get_serial_sequence('public.development_stage', 'stage_id'),
    COALESCE((SELECT MAX(stage_id) FROM public.development_stage), 1)
);

-- H.2: Re-seed biological_property with new numeric stage_id references
INSERT INTO public.biological_property (property_id, stage_id, property_label, data_type, is_critical, created_at, modified_at)
VALUES
    -- S1 (Intake) → stage_id = 2
    ('s1_mass',       2, 'Egg Mass (g)',          'NUMERIC',      true,  NOW(), NOW()),
    ('s1_diameter',   2, 'Egg Diameter (mm)',     'NUMERIC',      true,  NOW(), NOW()),
    ('s1_condition',  2, 'Egg Condition',         'TEXT',         true,  NOW(), NOW()),

    -- S2-Spot → stage_id = 3
    ('s2_molding',        3, 'Molding (0-4)',        'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_chalking',       3, 'Chalking (0-2)',       'INTEGER_0_2', true,  NOW(), NOW()),
    ('s2_vascularity',    3, 'Vascularity Present',  'BOOLEAN',     true,  NOW(), NOW()),
    ('s2_dented',         3, 'Dented (0-4)',         'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_discolored',     3, 'Discolored',           'BOOLEAN',     false, NOW(), NOW()),

    -- S2-Band → stage_id = 4
    ('s2_molding_band',       4, 'Molding (0-4)',        'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_chalking_band',      4, 'Chalking (0-2)',       'INTEGER_0_2', true,  NOW(), NOW()),
    ('s2_vascularity_band',   4, 'Vascularity Present',  'BOOLEAN',     true,  NOW(), NOW()),
    ('s2_dented_band',        4, 'Dented (0-4)',         'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_discolored_band',    4, 'Discolored',           'BOOLEAN',     false, NOW(), NOW()),

    -- S2-Full → stage_id = 5
    ('s2_molding_full',       5, 'Molding (0-4)',        'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_chalking_full',      5, 'Chalking (0-2)',       'INTEGER_0_2', true,  NOW(), NOW()),
    ('s2_vascularity_full',   5, 'Vascularity Present',  'BOOLEAN',     true,  NOW(), NOW()),
    ('s2_dented_full',        5, 'Dented (0-4)',         'INTEGER_0_4', false, NOW(), NOW()),
    ('s2_discolored_full',    5, 'Discolored',           'BOOLEAN',     false, NOW(), NOW()),

    -- S3 → stage_id = 6
    ('s3_molding',            6, 'Molding (0-4)',        'INTEGER_0_4', false, NOW(), NOW()),
    ('s3_chalking',           6, 'Chalking (0-2)',       'INTEGER_0_2', true,  NOW(), NOW()),
    ('s3_vascularity',        6, 'Vascularity Present',  'BOOLEAN',     true,  NOW(), NOW()),
    ('s3_leaking',            6, 'Leaking (0-4)',        'INTEGER_0_4', true,  NOW(), NOW()),
    ('s3_dented',             6, 'Dented (0-4)',         'INTEGER_0_4', false, NOW(), NOW()),
    ('s3_discolored',         6, 'Discolored',           'BOOLEAN',     false, NOW(), NOW()),
    ('s3_moisture_deficit',   6, 'Moisture Deficit',     'NUMERIC',     false, NOW(), NOW()),
    ('s3_water_added',        6, 'Water Added (mL)',     'NUMERIC',     false, NOW(), NOW()),

    -- S4-C → stage_id = 7
    ('s4_molding',            7, 'Molding (0-4)',        'INTEGER_0_4', false, NOW(), NOW()),
    ('s4_chalking',           7, 'Chalking (0-2)',       'INTEGER_0_2', true,  NOW(), NOW()),
    ('s4_vascularity',        7, 'Vascularity Present',  'BOOLEAN',     true,  NOW(), NOW()),
    ('s4_leaking',            7, 'Leaking (0-4)',        'INTEGER_0_4', true,  NOW(), NOW()),
    ('s4_dented',             7, 'Dented (0-4)',         'INTEGER_0_4', false, NOW(), NOW()),
    ('s4_discolored',         7, 'Discolored',           'BOOLEAN',     false, NOW(), NOW()),
    ('s4_moisture_deficit',   7, 'Moisture Deficit',     'NUMERIC',     false, NOW(), NOW()),
    ('s4_water_added',        7, 'Water Added (mL)',     'NUMERIC',     false, NOW(), NOW()),

    -- S4-Motion → stage_id = 9
    ('s4_motion',    9, 'Motion Observed',    'BOOLEAN', true, NOW(), NOW()),
    ('s4_pipping',   9, 'Pipping Observed',   'BOOLEAN', true, NOW(), NOW()),

    -- S5 → stage_id = 10
    ('s5_emerging',  10, 'Actively Emerging',          'BOOLEAN', true, NOW(), NOW()),
    ('s5_yolk_sac',  10, 'External Yolk Sac Present',  'BOOLEAN', true, NOW(), NOW()),

    -- S6-YA1 → stage_id = 11
    ('s6_weight',     11, 'Weight (g)',              'NUMERIC', true, NOW(), NOW()),
    ('s6_umbilical',  11, 'Umbilical Healed',        'BOOLEAN', true, NOW(), NOW()),
    ('s6_feeding',    11, 'Feeding Independently',   'BOOLEAN', true, NOW(), NOW());

-- ============================================================================
-- DONE: Commit the transaction
-- ============================================================================
COMMIT;
