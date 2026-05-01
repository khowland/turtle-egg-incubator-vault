-- CR-20260430-194500: Phase 6.1 — Add bin_code column to bin table
-- This is a transitional column; full UUID migration deferred to CR-20260501-PK-MIGRATION
ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS bin_code text;
UPDATE public.bin SET bin_code = bin_id WHERE bin_code IS NULL;
