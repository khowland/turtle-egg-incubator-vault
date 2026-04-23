# Supplemental Intake & Clinical Metadata Deployed
## Date: 2026-04-22

**Feature:** Supplemental Intake (Laying Mother) & JSONB Analytics
**Actions Taken:**
1. Added `clinical_metadata` JSONB column to `intake` table for analytical covariate tracking (Collection Method, Condition).
2. Created `vault_supplemental_intake` RPC to handle atomic additions to existing mothers.
3. Updated `2_New_Intake.py` with UI toggle for Initial vs Supplemental intake modes.
4. Resolved CR #1 (Post-mortem Salvage -> Harvested).

**Compliance:** Adheres to S1 baseline requirements and atomic RPC mandates.
