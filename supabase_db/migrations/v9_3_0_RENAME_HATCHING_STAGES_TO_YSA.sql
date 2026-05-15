-- v9_3_0_RENAME_HATCHING_STAGES_TO_YSA.sql
-- CR-20260514: Terminological remediation for hatching stages and vector DB initialization.

-- 1. Initialize Vector Storage for Expert Testing
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.clinical_audit_vectors (
    id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    content text NOT NULL,
    metadata jsonb,
    embedding vector(1536),
    created_at timestamptz DEFAULT now()
);

-- 2. Remediate Hatching Stage Terminology (YA -> YSA)
-- First, insert new stages to allow reference updates
INSERT INTO public.development_stage (stage_id, label, description, ordinal_rank, sub_code, created_at, modified_at)
VALUES
    ('S6-YSA1', 'Hatchling — Yolk Sack Absorbed 1', 'Post-hatch; full external yolk sac', 6, 'YSA1', NOW(), NOW()),
    ('S6-YSA2', 'Hatchling — Yolk Sack Absorbed 2', 'Post-hatch; half yolk sac absorbed', 6, 'YSA2', NOW(), NOW()),
    ('S6-YSA3', 'Hatchling — Yolk Sack Absorbed 3', 'Fully Absorbed (Buttoned-up); Biosecurity Gate for Export', 6, 'YSA3', NOW(), NOW())
ON CONFLICT (stage_id) DO UPDATE SET
    label = EXCLUDED.label,
    description = EXCLUDED.description;

-- Update existing egg records
UPDATE public.egg 
SET current_stage = CASE 
    WHEN current_stage = 'S6-YA1' THEN 'S6-YSA1'
    WHEN current_stage = 'S6-YA2' THEN 'S6-YSA2'
    WHEN current_stage = 'S6-YA3' THEN 'S6-YSA3'
    ELSE current_stage 
END
WHERE current_stage LIKE 'S6-YA%';

-- Update existing observation records
UPDATE public.egg_observation 
SET stage_id = CASE 
    WHEN stage_id = 'S6-YA1' THEN 'S6-YSA1'
    WHEN stage_id = 'S6-YA2' THEN 'S6-YSA2'
    WHEN stage_id = 'S6-YA3' THEN 'S6-YSA3'
    ELSE stage_id 
END
WHERE stage_id LIKE 'S6-YA%';

-- Update biological property mappings
UPDATE public.biological_property
SET stage_id = CASE 
    WHEN stage_id = 'S6-YA1' THEN 'S6-YSA1'
    WHEN stage_id = 'S6-YA2' THEN 'S6-YSA2'
    WHEN stage_id = 'S6-YA3' THEN 'S6-YSA3'
    ELSE stage_id 
END
WHERE stage_id LIKE 'S6-YA%';

-- Clean up legacy stages
DELETE FROM public.development_stage 
WHERE stage_id IN ('S6-YA1', 'S6-YA2', 'S6-YA3');

COMMENT ON TABLE public.clinical_audit_vectors IS 'Clinical Memory for Expert QA probing and adversarial biological testing.';
