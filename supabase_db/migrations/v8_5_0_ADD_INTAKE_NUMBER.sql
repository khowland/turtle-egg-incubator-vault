-- CR-20260429-225412: Add intake_number INTEGER column to intake table
-- Resolves bin code generation race conditions by providing a server-side counter
ALTER TABLE public.intake ADD COLUMN IF NOT EXISTS intake_number INTEGER;

-- Populate existing rows with row_number() over species_id to seed values
-- Only runs if column was just added (no existing values)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public'
          AND table_name = 'intake' 
          AND column_name = 'intake_number'
    ) THEN
        UPDATE public.intake i
        SET intake_number = sub.rn
        FROM (
            SELECT intake_id, 
                   ROW_NUMBER() OVER (PARTITION BY species_id ORDER BY created_at) AS rn
            FROM public.intake
        ) sub
        WHERE i.intake_id = sub.intake_id
          AND i.intake_number IS NULL;
    END IF;
END $$;

-- Add unique index to prevent duplicate intake numbers per species
CREATE UNIQUE INDEX IF NOT EXISTS idx_intake_species_number 
    ON public.intake(species_id, intake_number)
    WHERE species_id IS NOT NULL AND intake_number IS NOT NULL;
