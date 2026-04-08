-- =============================================================================
-- Migration: 20260408_v7_2_0_pivot.sql
-- Project:   Incubator Vault v7.2.0 — Wildlife In Need Center (WINC)
-- Purpose:   Implementing Neonate Pivot, Bin Weight Hydration, and 
--            Hatchling_Ledger tracking.
-- =============================================================================

-- 1. Create Hatchling_Ledger Table (§3.4)
CREATE TABLE IF NOT EXISTS hatchling_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    egg_id UUID REFERENCES egg(id),
    mother_id UUID REFERENCES mother(id),
    hatch_date DATE DEFAULT CURRENT_DATE,
    hatch_weight_g DECIMAL(10,2),
    vitality_score TEXT, -- Yolk sac status, etc.
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 2. Update Bin Table for Restorative Hydration (§3.2)
ALTER TABLE bin ADD COLUMN IF NOT EXISTS target_total_weight_g DECIMAL(10,2);
ALTER TABLE bin ADD COLUMN IF NOT EXISTS shelf_location TEXT;
ALTER TABLE bin ADD COLUMN IF NOT EXISTS substrate TEXT;

-- 3. Update EggObservation for Weight Tracking
ALTER TABLE egg_observation ADD COLUMN IF NOT EXISTS bin_weight_at_obs_g DECIMAL(10,2);
ALTER TABLE egg_observation ADD COLUMN IF NOT EXISTS water_added_ml DECIMAL(10,2);
ALTER TABLE egg_observation ADD COLUMN IF NOT EXISTS moisture_deficit_g DECIMAL(10,2);

-- 4. Mid-Season Lock Support: Function to check for active eggs
CREATE OR REPLACE FUNCTION check_active_eggs() 
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM egg 
        WHERE status = 'Active' 
        AND is_deleted = FALSE
    );
END;
$$ LANGUAGE plpgsql;

-- 5. Audit Triggers for New Table
CREATE TRIGGER update_hatchling_ledger_modtime
    BEFORE UPDATE ON hatchling_ledger
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
