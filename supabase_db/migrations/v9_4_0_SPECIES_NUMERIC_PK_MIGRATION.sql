-- v9_4_0_SPECIES_NUMERIC_PK_MIGRATION.sql
-- CR-20260514: Align species table with Numeric Surrogate Key standard (Req §1.6)

BEGIN;

-- 1. Preparation: Drop FKs referencing species.species_id
ALTER TABLE public.intake DROP CONSTRAINT IF EXISTS intake_species_id_fkey;

-- 2. Transform Species Table
-- Move the string-based ID to the species_code column (if not already there)
UPDATE public.species SET species_code = species_id WHERE species_code IS NULL;

-- Rename and Add Numeric ID
ALTER TABLE public.species RENAME COLUMN species_id TO legacy_code;
ALTER TABLE public.species ADD COLUMN species_id_new BIGINT GENERATED ALWAYS AS IDENTITY;

-- 3. Update Intake Table FK
ALTER TABLE public.intake ADD COLUMN species_id_new BIGINT;

-- Map existing intakes to new numeric IDs
UPDATE public.intake i
SET species_id_new = s.species_id_new
FROM public.species s
WHERE i.species_id = s.legacy_code;

-- 4. Finalize Schema
ALTER TABLE public.intake DROP COLUMN species_id;
ALTER TABLE public.intake RENAME COLUMN species_id_new TO species_id;

ALTER TABLE public.species DROP CONSTRAINT IF EXISTS species_pkey CASCADE;
ALTER TABLE public.species DROP COLUMN legacy_code;
ALTER TABLE public.species RENAME COLUMN species_id_new TO species_id;
ALTER TABLE public.species ADD CONSTRAINT species_pkey PRIMARY KEY (species_id);

-- Re-add FK with numeric alignment
ALTER TABLE public.intake 
    ADD CONSTRAINT intake_species_id_fkey 
    FOREIGN KEY (species_id) REFERENCES public.species(species_id);

-- 5. Update RPCs for Numeric PK alignment
-- (The RPC vault_finalize_intake will now receive a numeric species_id)

COMMIT;
