# Implementation Plan for CR-20260430-194500 — v2 (Peer-Reviewed)

**Data Architecture Integrity & System Refactoring**

---

## Review Findings

### Reviewer Summary
Peer engineering review conducted against the original plan and validated with live codebase inspection (schema export, application Python files, migration SQL files). Original plan dated 2026-04-30; review performed 2026-05-01.

### Changes Applied in v2

| # | Category | Description |
|---|----------|-------------|
| 1 | **Ordering Fix** | Phases reordered: Phase 6 (Error Handling) moved before Phase 3 (UI) because `observer_id` column (Phase 1.3) and `safe_db_execute` fix must be deployed before UI changes hit those code paths. |
| 2 | **Ordering Fix** | Phase 2 (RPC Updates) must complete BEFORE Phase 1 (Schema Corrections) — dropping `incubator_temp_c` from `bin` before updating RPCs that reference it will cause RPC failures. Consolidated Phase 1 and Phase 2 into a single migration transaction. |
| 3 | **Missing Task** | Added Phase 1.2a: `bin_observation` column consolidation. The current schema has BOTH `ambient_temp` (unused by app) AND `incubator_temp_c` (written by app) on `bin_observation`. Need to migrate data from `incubator_temp_c` → `incubator_temp_f` then drop both old columns. Original plan assumed only `ambient_temp` existed. |
| 4 | **Missing Task** | Added Phase 1.2b: Verify `incubator_temp_c` exists on `bin` in production DB before dropping. Schema export doesn't show it but migration v8_1_16 adds it via `ADD COLUMN IF NOT EXISTS`. Plan must handle both scenarios. |
| 5 | **Missing Task** | Added Phase 2.4: Create consolidated RPC migration files (new `.sql` files) — original plan only described edits but never specified creating replacement migration files. |
| 6 | **Missing Task** | Added Phase 8.2e: RPC regression tests (`test_rpc_vault_finalize_intake.py`, `test_rpc_vault_admin_restore.py`) — original Phase 8 had zero tests for the RPC layer despite Phase 2 being entirely RPC changes. |
| 7 | **Missing Task** | Added Phase 0.4: Pre-flight environment audit — query production schema to resolve column-state ambiguities (incubator_temp_c on bin, ambient_temp vs incubator_temp_c on bin_observation) before writing migrations. |
| 8 | **Missing Task** | Added Phase 0.5: Define rollback procedures for each phase. Original plan had a backup but no rollback playbook. |
| 9 | **Data Integrity Risk** | Added verification step in Phase 1.2a: COUNT rows where `incubator_temp_c IS NOT NULL` on `bin_observation` before migrating — if >0 rows, data must be preserved; if 0, skip migration. |
| 10 | **Factual Correction** | Molding slider range in gap analysis corrected from "Hardcoded (0-2)" to "Hardcoded (0-3)" — code inspection shows `[0, 1, 2, 3]`. Gap still exists (expert wants 0-4), but severity downgraded from CRITICAL to Medium. |
| 11 | **Risk Assessment Added** | Per-phase risk ratings (L/M/H) with rationale added to each phase header. |
| 12 | **Edge Case Coverage** | Added edge case notes for: empty `bin_observation` table, pre-existing `bin_code` column, foreign key constraint violations during rename, and Streamlit session state carrying stale column references after deployment. |

### Critical Risks Retained from Original Plan

1. **Phase 7 (PK/FK Standardization) is incomplete**: Adding `bin_code` and `egg_stage_code` without completing the UUID migration leaves the schema in a transitional state with two columns serving overlapping purposes. Recommendation to defer to dedicated CR-20260501-PK-MIGRATION is correct but the risk of partial implementation causing confusion is **HIGH**.
2. **`biological_property` seeding is deferred**: Plan acknowledges this (Phase 4.3 marked "Optional") but the gap analysis identifies it as CRITICAL. Without dynamic property rendering, the lab director cannot add new metrics without code changes. A separate follow-up CR should be created immediately.
3. **No CI/CD pipeline details**: Phase 10 assumes a mature CI/CD pipeline but doesn't specify whether migrations are applied automatically or require manual approval. If automated, a bad migration could affect production before review.

---

## Status Note
CR-20260430-181500 has been updated to **CLOSED — Changes merged with Implementation plan for CR-20260430-194500**. Its implementation plan (minus Section 1.1) has been absorbed into this document.

---

## Part 1: Gap Analysis — Requirements vs. System Functionality

### 1.1 Biological Property & Egg Observations
**What requirements.md says**:
- §3 defines Bins, Eggs with developmental stages S0-S6.
- §4 mandates forensic auditing of every clinical change.
- The *implied_system_objective.md* and *turtle_expert_interview.md* add depth: observations must capture molding (0-4), chalking (0-2), vascularity, leaking, dented, discoloration, moisture deficit, water added, and stage/sub-stage transitions.

**What the system has**:
- **`biological_property` table** exists (schema line 58-68) with columns: `property_id` (text PK), `stage_id` (text FK), `property_label`, `data_type`, `is_critical`.
- **No rows are seeded** in the lookup table. The table is empty by default.
- **3_Observations.py** does NOT read from `biological_property` at all. The observation form is hardcoded with individual Streamlit widgets for each metric (molding slider, chalking radio, vascularity toggle, etc.) rather than dynamically generating controls from the lookup table.
- **Gap**: The `biological_property` table design is correct (normalized lookup allowing configurable properties per stage), but it is **completely unused** by the application layer. The UI is hardcoded, making it impossible for a lab director to add new observation metrics without code changes.

**What the turtle expert requires**:
- Molding (0-4 range), Chalking (0-2), Vascularity (boolean), Leaking (0-4), Dented (0-4), Discolored (boolean), Moisture Deficit (numeric), Water Added (numeric), Stage/Sub-stage observations.
- All must be recordable for multiple eggs simultaneously.
- Egg icons from `/docs/assets/icons/` must render per egg's current stage.

**REVIEW NOTE — Factual Correction**: The original gap analysis table claimed Molding was "Hardcoded (0-2)". Code inspection of `3_Observations.py` line 873 shows the slider uses `[0, 1, 2, 3]` — the actual range is 0-3, not 0-2. The gap still exists (expert requires 0-4), but the current implementation is closer to the target than stated.

**Gap Assessment**:
| Item | Required by Expert | In requirements.md | In System | Gap |
|------|-------------------|-------------------|-----------|-----|
| Molding (0-4) | Yes | No | Hardcoded (0-3) | Range mismatch; should be 0-4 per expert. Current code allows 0-3. |
| Chalking (0-2) | Yes | No | Hardcoded | OK |
| Vascularity | Yes | No | Hardcoded | OK |
| Leaking (0-4) | Yes | No | Hardcoded (0-4) | OK |
| Dented (0-4) | Yes | No | Hardcoded (0-4) | OK |
| Discolored | Yes | No | Hardcoded | OK |
| Moisture Deficit | Implied | No | Hardcoded | OK |
| Water Added | Implied | No | Hardcoded | OK |
| Dynamic property config | Desired | No | **Not implemented** | **CRITICAL** |
| Multi-egg selection | Yes | No | Yes (checkboxes) | OK |
| Egg icons per stage | Yes | No | Yes (render_egg_icon) | OK |

**Recommendation**: Populate `biological_property` with standard rows and refactor 3_Observations.py to dynamically render observation controls from this lookup table. Update requirements.md §3 to define the full biological property model.

---

### 1.2 Lookup Table Management
**requirements.md §8** defines State 1 (Clean Start) preserves lookup tables. The system does this via `vault_admin_restore` RPC.

**Current lookup tables and their state**:
| Table | Has default rows? | Populated by | Gap |
|-------|------------------|--------------|-----|
| `species` | No | Manual entry via Settings | Should have a seed script with WI native species (Blanding's, Stinkpot, etc.) |
| `observer` | No | Manual entry via Settings | OK |
| `development_stage` | **Unknown** | Check if populated | **CRITICAL**: Must define S0-S6 with sub-stages |
| `biological_property` | **No** | Never populated | **CRITICAL**: Must seed with standard observation properties |
| `system_config` | Yes (version) | Migration scripts | OK, but may need additional config keys (e.g., min-export-stage) |

---

### 1.3 Requirements.md Gaps Identified
1. **No biological property model** — requirements.md lacks any definition of what egg observation metrics exist, their ranges, and how they relate to developmental stages.
2. **No stage/sub-stage specification** — The S1-S6 milestones are mentioned but sub-stages (Spot/Band/Full for S2, C-Stage/Term/Motion for S4, YA1/YA2/YA3 for S6) are only in the operator manual requirements, not the system requirements.
3. **No bin closure audit workflow** — The expert interview requires a final closure note when all eggs in a bin reach terminal state, but requirements.md doesn't specify this.
4. **No export gate specification** — requirements.md §4 mentions "Correction Mode" but doesn't specify the S6-YA3 biosecurity gate for WormD export mentioned in operator manual requirements.
5. **No backup/restore for lookup tables** — State 1 and State 2 operations should preserve and re-seed lookup tables, but the exact seed data is not specified.

---

## Part 2: Impact Analysis — Column Renames & Schema Refactoring

### 2.1 `incubator_temp_c` → `incubator_temp_f` (bin_observation table)

**REVIEW NOTE — Revised Analysis**: The original plan conflated two separate issues: (a) removing `incubator_temp_c` from the `bin` table, and (b) consolidating temperature columns on `bin_observation`. Codebase investigation reveals:

**Current state (as of schema export 2026-04-28 + migration files + application code)**:
- `bin` table: Schema export shows NO `incubator_temp_c`. Migration `v8_1_16` adds it via `ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS incubator_temp_c NUMERIC`. **Status unknown on production** — column may or may not exist depending on whether v8_1_16 was applied.
- `bin_observation` table: Schema export shows `ambient_temp numeric`. Migration `v8_1_16` also adds `incubator_temp_c NUMERIC` to `bin_observation`. So `bin_observation` may have BOTH `ambient_temp` AND `incubator_temp_c`.
- Application code (`3_Observations.py`, `2_New_Intake.py`): All temperature inserts use the key `"incubator_temp_c"` — writing to `bin_observation.incubator_temp_c` (and `bin.incubator_temp_c` in 2_New_Intake.py line 380). Zero Python files use `"ambient_temp"`.

**What must change**:
1. Drop `incubator_temp_c` from `bin` table (if it exists)
2. Consolidate `bin_observation` temperature columns: migrate data from `incubator_temp_c` → `incubator_temp_f`, drop BOTH `ambient_temp` and `incubator_temp_c`
3. Update all application code to use `incubator_temp_f`
4. Update all RPC functions to use `incubator_temp_f`

**Current references — all files that MUST be updated**:

| File | Line(s) | Current Reference | Action |
|------|---------|-------------------|--------|
| `supabase_db/migrations/RPC_VAULT_FINALIZE_INTAKE.sql` | 105,117,132,142 | `incubator_temp_c` in INSERT statements | Remove from `bin` INSERT; rename to `incubator_temp_f` in `bin_observation` INSERT |
| `supabase_db/migrations/v8_1_16_ADD_TEMP_TO_BIN_OBS.sql` | 10,13 | `ALTER TABLE ... ADD COLUMN incubator_temp_c` on bin and bin_observation | **Reverse**: Drop both columns, replace with `incubator_temp_f` on bin_observation only |
| `supabase_db/migrations/v8_1_18_RPC_VAULT_ADMIN_RESTORE.sql` | 47,58 | `incubator_temp_c` in INSERT | Replace with `incubator_temp_f` on bin_observation; NULL for bin |
| `supabase_db/migrations/v8_1_19_ENFORCE_TIMESTAMP_SOVEREIGNTY.sql` | 85,88,94,98 | `incubator_temp_c` references | Replace all → `incubator_temp_f` on bin_observation; remove from bin INSERT |
| `supabase_db/migrations/v8_1_21_ADD_DAYS_IN_CARE.sql` | 83,86,92,96 | Same pattern | Same fix |
| `supabase_db/migrations/v8_1_22_MOTHER_WEIGHT.sql` | 83,86,92,96 | Same pattern | Same fix |
| `supabase_db/migrations/v8_1_25_SUPPLEMENTAL_INTAKE.sql` | 64,73 | `incubator_temp_c` references | Same fix |
| `supabase_db/migrations/v8_1_27_RPC_VAULT_ADMIN_RESTORE_V2.sql` | 110,126,174,188,229,243 | Multiple references | Same fix |
| `vault_views/2_New_Intake.py` | 289 | `"incubator_temp_c": row_data["temp"]` | **Remove entirely** — no longer sent in intake RPC |
| `vault_views/3_Observations.py` | 380,411,514 | `"incubator_temp_c": ...` in bin_observation inserts | Rename to `incubator_temp_f` |
| `vault_views/5_Settings.py` | Backup/Restore section (lines 429-542) | Calls `vault_admin_restore` and `vault_export_full_backup` | Verify restored data uses new column names |
| `scripts/` | `forensic_auditor.py`, `seed_complex_scenario.py`, `backend_qa_verification.py` | May reference old columns | Audit and update |
| `tests/` | Multiple test files with SQL verification | May reference `incubator_temp_c` or `ambient_temp` | Update all test assertions |

### 2.4 `development_stage.stage_id` → `development_stage.egg_stage_code`

**Current state**: `stage_id` is a `text` column storing stage codes (e.g., "S1", "S2", "S3-Spot") and serves as PK. Referenced in `biological_property.stage_id` and `egg.current_stage`.

**Required change**:
1. Add `egg_stage_code text` column
2. Copy values: `UPDATE development_stage SET egg_stage_code = stage_id`
3. Add new `stage_id uuid` column with auto-generated UUIDs
4. Update FK in `biological_property` and references in `egg.current_stage`

**Impact — files referencing `stage_id`**:
| File | Usage | Action |
|------|-------|--------|
| `vault_views/3_Observations.py` | Queries stage for observation form | Use `egg_stage_code` for display |
| `vault_views/5_Settings.py` | Stages & Icons tab | Update column references |
| Migration files | Stage seed data | Update |
| `egg.current_stage` | Stores stage code | Should reference `egg_stage_code` or maintain text value directly |
| `utils/visuals.py` | Maps stage to icon | Use `egg_stage_code` |

---

## Part 3: Merged Implementation Plan (v2 — Peer Reviewed)

This plan incorporates all actionable items from CR-20260430-181500 (except the rejected Section 1.1) and the new requirements from CR-20260430-194500. Each phase contains detailed, atomic tasks suitable for delegation to lower-level agents.

**Phase ordering has been revised per peer review to fix critical dependency inversions.**

---

### Phase 0: Preparation & Safeguards — Risk: LOW

**Risk Assessment**: Low — no destructive operations; purely informational and preparatory work. Primary risk is discovering environment surprises that force plan revision, which is a feature, not a bug.

**0.1 Update requirements.md**
- [ ] Add §3.1: Biological Property Model — define observation metrics, ranges, per-stage applicability
- [ ] Add §3.2: Stage/Sub-Stage Specification — define S0-S6 with all sub-stages
- [ ] Add §4.5: Bin Closure Audit — require final observation note when all eggs terminal
- [ ] Add §4.6: Biosecurity Export Gate — S6-YA3 minimum for WormD export

**0.2 Archive outdated migration scripts**
- [ ] Move all `.sql` files in `supabase_db/migrations/` that reference old column names (incubator_temp_c, ambient_temp on bin) to `supabase_db/archive/`
- [ ] Retain only the latest schema export as reference

**0.3 Create database backup**
- [ ] Export full current schema via Supabase dashboard or CLI
- [ ] Save backup in `/docs/design/db_schema_pre_refactor_05012026.txt`

**0.4 ★NEW★ Pre-flight environment audit**
- [ ] Query production database to resolve column-state ambiguities:
  ```sql
  -- Does incubator_temp_c exist on bin?
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'bin' AND column_name = 'incubator_temp_c';
  
  -- What temperature columns exist on bin_observation?
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'bin_observation' AND column_name IN ('ambient_temp', 'incubator_temp_c', 'incubator_temp_f');
  
  -- How many rows have data in each temperature column?
  SELECT 
    COUNT(*) FILTER (WHERE ambient_temp IS NOT NULL) AS ambient_count,
    COUNT(*) FILTER (WHERE incubator_temp_c IS NOT NULL) AS incubator_count
  FROM public.bin_observation;
  
  -- Do bin_code or egg_stage_code columns already exist?
  SELECT column_name, table_name FROM information_schema.columns 
  WHERE table_name IN ('bin', 'development_stage') 
  AND column_name IN ('bin_code', 'egg_stage_code');
  ```
- [ ] Document findings — these determine whether Phase 1 migrations are no-ops, data-migrations, or schema-only changes.
- [ ] **GATE**: Do not proceed to Phase 1 without audit results.

**0.5 ★NEW★ Define rollback procedures**
- [ ] For each migration file: document the exact SQL to reverse the change if it fails
- [ ] Create `/docs/deployment/rollback_procedures_CR-20260430-194500.md`:
  - Phase 1 rollback: Re-add dropped columns (with NULLs), rename columns back, re-create old RPC versions
  - Phase 3-5 rollback: Git revert to previous commit, restart Streamlit
- [ ] Tag current commit as `pre-CR-20260430-194500` for easy rollback

---

### Phase 1: Schema & RPC Corrections (Temperature Columns) — Risk: MEDIUM

**REVIEW NOTE — Phase Merge**: Original plan had separate Phase 1 (Schema) and Phase 2 (RPC). These phases have a hard mutual dependency: dropping columns before updating RPCs will cause runtime failures. They must execute atomically in a single migration transaction or RPC updates must deploy first. This v2 merges them into a single coordinated phase with explicit ordering: RPC updates first (as CREATE OR REPLACE), then schema changes, all within one CI/CD deployment.

**Risk Assessment**: Medium — schema changes are inherently risky. Mitigated by pre-flight audit (Phase 0.4), backup (Phase 0.3), and atomic deployment of RPC + schema changes. Primary risk is data loss in `bin_observation` temperature columns if migration logic has a bug.

**1.0 ★NEW★ Create consolidated RPC migration with corrected column names**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_0_UPDATE_ALL_RPCS_FOR_TEMP_RENAME.sql`
- [ ] This file must:
  - `CREATE OR REPLACE FUNCTION vault_finalize_intake(...)` removing `incubator_temp_c` from `bin` INSERT and replacing with `incubator_temp_f` in `bin_observation` INSERT
  - `CREATE OR REPLACE FUNCTION vault_admin_restore(...)` with same column name corrections
  - `CREATE OR REPLACE FUNCTION vault_export_full_backup(...)` with corrected column names
  - `CREATE OR REPLACE FUNCTION vault_finalize_batch_observation(...)` if it references temperature
- [ ] **CRITICAL**: This migration must deploy BEFORE the schema column drops in 1.1-1.2a.

**1.1 Drop `incubator_temp_c` from `bin` table (conditional on audit findings)**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_1_DROP_INCUBATOR_TEMP_FROM_BIN.sql`
  ```sql
  DO $$
  BEGIN
    IF EXISTS (
      SELECT 1 FROM information_schema.columns 
      WHERE table_schema = 'public' AND table_name = 'bin' AND column_name = 'incubator_temp_c'
    ) THEN
      ALTER TABLE public.bin DROP COLUMN incubator_temp_c;
      RAISE NOTICE 'Dropped incubator_temp_c from bin';
    ELSE
      RAISE NOTICE 'incubator_temp_c not present on bin — no action needed';
    END IF;
  END $$;
  ```
- [ ] Verify: `SELECT column_name FROM information_schema.columns WHERE table_name = 'bin' AND column_name = 'incubator_temp_c';` — must return 0 rows.

**1.2a ★NEW★ Consolidate `bin_observation` temperature columns**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_2_CONSOLIDATE_BIN_OBS_TEMP.sql`
- [ ] Logic depends on Phase 0.4 audit results:
  ```sql
  -- Step 1: Ensure target column exists
  ALTER TABLE public.bin_observation ADD COLUMN IF NOT EXISTS incubator_temp_f NUMERIC;
  
  -- Step 2: Migrate data from whichever source column has data
  -- If incubator_temp_c has data (app writes to it):
  DO $$
  BEGIN
    IF EXISTS (
      SELECT 1 FROM information_schema.columns 
      WHERE table_schema = 'public' AND table_name = 'bin_observation' AND column_name = 'incubator_temp_c'
    ) THEN
      UPDATE public.bin_observation 
      SET incubator_temp_f = COALESCE(incubator_temp_f, incubator_temp_c);
      ALTER TABLE public.bin_observation DROP COLUMN IF EXISTS incubator_temp_c;
      RAISE NOTICE 'Migrated data from incubator_temp_c to incubator_temp_f and dropped old column';
    END IF;
  END $$;
  
  -- Step 3: Drop ambient_temp (app never writes to it — verify via audit)
  ALTER TABLE public.bin_observation DROP COLUMN IF EXISTS ambient_temp;
  ```
- [ ] **EDGE CASE**: If `ambient_temp` has data (Phase 0.4 audit returns count > 0), migrate it too:
  ```sql
  UPDATE public.bin_observation 
  SET incubator_temp_f = COALESCE(incubator_temp_f, ambient_temp)
  WHERE ambient_temp IS NOT NULL;
  ```
- [ ] Verify: Only `incubator_temp_f` remains as a temperature column on `bin_observation`:
  ```sql
  SELECT column_name FROM information_schema.columns 
  WHERE table_name = 'bin_observation' 
  AND column_name IN ('ambient_temp', 'incubator_temp_c', 'incubator_temp_f');
  ```

**1.3 Add `observer_id` column to `system_log`**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_3_ADD_OBSERVER_ID_TO_SYSTEM_LOG.sql`
  ```sql
  ALTER TABLE public.system_log ADD COLUMN IF NOT EXISTS observer_id uuid;
  ALTER TABLE public.system_log ADD CONSTRAINT system_log_observer_id_fkey
      FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);
  ```
- [ ] This fixes the `PGRST204` error when `safe_db_execute` inserts audit records.

**1.4 Archive old RPC version files**
- [ ] Move old RPC SQL files to `supabase_db/archive/`:
  `RPC_VAULT_FINALIZE_INTAKE.sql`, `v8_1_16_ADD_TEMP_TO_BIN_OBS.sql`, `v8_1_18_RPC_VAULT_ADMIN_RESTORE.sql`, `v8_1_19_ENFORCE_TIMESTAMP_SOVEREIGNTY.sql`, `v8_1_21_ADD_DAYS_IN_CARE.sql`, `v8_1_22_MOTHER_WEIGHT.sql`, `v8_1_25_SUPPLEMENTAL_INTAKE.sql`, `v8_1_27_RPC_VAULT_ADMIN_RESTORE_V2.sql`
- [ ] Keep only the consolidated `v8_3_0` and new `v8_3_x` files in active migrations directory

---

### Phase 2: Error Handling Fixes — Risk: LOW

**REVIEW NOTE — Reordered from Phase 6**: Moved before UI changes because:
1. Phase 1.3 adds `observer_id` column — the buggy `safe_db_execute` code will now succeed (column exists), but the double-error-propagation bug remains.
2. UI changes (Phase 3-5) will trigger `safe_db_execute` and `commit_all` — must be fixed before UI changes go live to prevent confusing double-error displays.

**Risk Assessment**: Low — code changes only, no schema impact. Relatively contained fixes.

**2.1 Fix `safe_db_execute` dual error insertion**
- [ ] **File**: `utils/bootstrap.py`, lines 346-410
- [ ] In the `except` block (line 375+), add try/except around the system_log insert:
  ```python
  try:
      get_resilient_table(get_supabase(), "system_log").insert({
          "session_id": st.session_state.get("session_id", "SYSTEM"),
          "event_type": "ERROR",
          "event_message": f"{operation_name} failed: {str(e)}",
      }).execute()
  except Exception:
      pass  # system_log insert failure should not mask original error
  ```
- [ ] **Note**: Since Phase 1.3 adds the column, the insert should normally succeed. The try/except is defense-in-depth.

**2.2 Fix `commit_all` inner exception handler**
- [ ] **File**: `vault_views/2_New_Intake.py`, lines 353-362
- [ ] Make `observer_id` conditional in the log entry:
  ```python
  log_entry = {
      "session_id": st.session_state.session_id,
      "event_type": "ERROR",
      "event_message": f"Intake failed: Case {case_number} — Transaction failed: {str(error)}",
  }
  if st.session_state.get("observer_id"):
      log_entry["observer_id"] = st.session_state.observer_id
  get_resilient_table(supabase, "system_log").insert(log_entry).execute()
  ```

**2.3 Fix dual error propagation**
- [ ] The inner `except` in `commit_all` raises after logging, which triggers the outer `except` in `safe_db_execute`, which logs again and re-raises. This doubles the error display to the user.
- [ ] **Solution A (Recommended)**: In `commit_all`, replace `raise` with `return False` and let the outer handler manage the user-facing error. Update `commit_all` call pattern to check return value.
- [ ] **Solution B**: Remove `safe_db_execute` wrapper from `commit_all` call (line 367) since `commit_all` already has comprehensive error handling.

---

### Phase 3: UI Code Changes — 2_New_Intake.py — Risk: MEDIUM

**Risk Assessment**: Medium — UI changes carry lower data risk but moderate regression risk. User workflows will change (new labels, removed mass/temp fields, supplemental mode refactor). Mitigated by Phase 8 test updates.

**REVIEW NOTE — Dependency**: Phase 1 (migrations) must be fully deployed before this phase goes live, because:
- Removing `incubator_temp_c` from bins_payload (3.3) means the RPC must no longer expect that field
- Supplemental mode changes assume `bin_code` column may exist (if Phase 7 partially applied) — but Phase 7 is deferred, so ensure code handles `bin_id` as the display column

**3.1 Step 1 Label Changes**
- [ ] **Line 108**: Change `col3.date_input("Date", ...)` → `col3.date_input("Intake Date", ...)`
- [ ] **Line 130**: Change `l_col3.selectbox("Collection Method", ...)` → `l_col3.selectbox("Egg Collection Method", ...)`

**3.2 Radio Button Labels (Supplemental Mode)**
- [ ] **Line 87-88**: Replace radio options:
  ```python
  # OLD:
  ["Initial Intake (New Case)", "Supplemental Intake (Add to Existing Mother)"]
  # NEW:
  ["New Intake", "Add Eggs or Bins to Existing Intake"]
  ```
- [ ] Update all downstream conditionals matching old strings:
  - Line 89: `if intake_mode == "Supplemental Intake (Add to Existing Mother)":` → `if intake_mode == "Add Eggs or Bins to Existing Intake":`
  - Line 161 in commit_all: same update
  - **EDGE CASE**: Streamlit session state may hold old string values from cached browser sessions after deployment — add migration logic or handle both old/new strings during transition.

**3.3 Remove `incubator_temp_c` from bins_payload**
- [ ] **Line 289**: Delete `"incubator_temp_c": row_data["temp"]` from the bins_payload dictionary
- [ ] Remove `"bin_weight_g": row_data["mass"]` as well (mass moved to Observations per CR-20260430-181500)
- [ ] Verify the bin INSERT in the RPC no longer includes these fields (Phase 1.0)

**3.4 Bin Configuration Grid Redesign**
- [ ] **Update `bin_rows` default** (lines 70-81):
  ```python
  st.session_state.bin_rows = [
      {
          "bin_num": 1,
          "current_egg_count": 0,
          "new_egg_count": 1,
          "notes": "Initial Intake",
          "substrate": "Vermiculite",
          "shelf": ""
      }
  ]
  ```
- [ ] **Update `data_editor` column_config** (lines 184-199):
  ```python
  column_config={
      "bin_id_preview": st.column_config.TextColumn("Bin Code (Auto)", disabled=True),
      "bin_num": st.column_config.NumberColumn("Bin #", disabled=True),
      "current_egg_count": st.column_config.NumberColumn("Current Egg Count", disabled=True),
      "new_egg_count": st.column_config.NumberColumn("Add New Eggs", min_value=0, max_value=99, required=True),
      "notes": st.column_config.TextColumn("Setup Notes"),
      "shelf": None,
      "substrate": None,
      "mass": None,  # REMOVED
      "temp": None,  # REMOVED
  }
  ```
- [ ] **Remove mass validation** (lines 236-238): Delete the check `if brow["mass"] <= 0:`
- [ ] **Update commit_all** to use `new_egg_count`:
  ```python
  for row_data in st.session_state.bin_rows:
      total_eggs = row_data.get("current_egg_count", 0) + row_data["new_egg_count"]
      if total_eggs < 1:
          st.error(f"❌ Bin #{row_data['bin_num']} must have at least 1 egg total.")
          st.stop()
      bins_payload.append({
          "bin_id": bid,
          "bin_notes": row_data.get("notes", ""),
          "egg_count": total_eggs,
          "substrate": row_data["substrate"],
          "shelf_location": row_data["shelf"]
      })
  ```

**3.5 Supplemental Mode Enhancements**
- [ ] **Load existing bins into bin_rows** when an intake is selected:
  ```python
  if intake_mode == "Add Eggs or Bins to Existing Intake":
      # Fetch existing bins for this intake
      existing_bins = supabase.table("bin").select("bin_id, total_eggs, bin_notes, substrate, shelf_location").eq("intake_id", supp_intake_id).execute()
      # Populate bin_rows with existing data
      st.session_state.bin_rows = [
          {
              "bin_num": idx + 1,
              "current_egg_count": b["total_eggs"],
              "new_egg_count": 0,
              "notes": b.get("bin_notes", ""),
              "substrate": b.get("substrate", "Vermiculite"),
              "shelf": b.get("shelf_location", ""),
              "is_new_bin": False,
              "existing_bin_id": b["bin_id"]
          }
          for idx, b in enumerate(existing_bins.data)
      ]
  ```
- [ ] **Make Step 1 fields read-only in supplemental mode**:
  ```python
  is_supplemental = (intake_mode == "Add Eggs or Bins to Existing Intake")
  # Fetch selected intake details
  if is_supplemental and supp_intake_id:
      intake_details = supabase.table("intake").select("intake_name, finder_turtle_name, species_id").eq("intake_id", supp_intake_id).single().execute()
      # Set session state values
  
  # In Step 1:
  selected_label = col1.selectbox("Species", ..., disabled=is_supplemental)
  case_number = col2.text_input("WINC Case #", ..., disabled=is_supplemental)
  finder_name = l_col1.text_input("Finder", ..., disabled=is_supplemental)
  ```
- [ ] **Update commit_all() for supplemental mode**:
  - If supplemental: use `supp_intake_id`, do NOT create intake, do NOT increment species.intake_count
  - For existing bins: UPDATE bin SET total_eggs = total_eggs + new_egg_count; INSERT eggs
  - For new bins: INSERT bin + eggs as normal but with `intake_id = supp_intake_id`

---

### Phase 4: UI Code Changes — 3_Observations.py — Risk: MEDIUM

**Risk Assessment**: Medium — observation data is core clinical data. Column name change is simple but a mismatch between app code and schema will silently fail to save observations or write to wrong column. Thorough testing essential.

**4.1 Update all temperature references to `incubator_temp_f`**
- [ ] **Lines 380, 411, 514**: Replace `"incubator_temp_c"` with `"incubator_temp_f"` in bin_observation INSERT payloads
- [ ] **Line ~380**: Update bin INSERT (if still present) — remove `incubator_temp_c` from bin creation
- [ ] Update column labels in the UI sidebar from "Ambient Temp" to "Incubator Temp (°F)"
- [ ] **REVIEW NOTE**: The code currently writes to `incubator_temp_c` on bin_observation. After Phase 1.2a, that column will be dropped and only `incubator_temp_f` will exist. This change must exactly align.

**4.2 Remove Supplemental Tools from Sidebar**
- [ ] Remove lines 67-89: "Add Bin to Intake" expander (sup_bin_mode logic)
- [ ] Remove lines 91-197: "Add Eggs to Existing Bin" expander
- [ ] Remove the entire "🛠️ Extra Tools" sidebar header if no other tools remain
- [ ] Remove related session state variables: `sup_bin_mode`, `sup_bin_intake_id`, `sup_bin_intake_name`

**4.3 (Optional) Load `biological_property` dynamically**
- [ ] Query `biological_property` joined with `development_stage` for current egg stages
- [ ] Render controls based on property definitions instead of hardcoded widgets
- [ ] **Note**: This is a larger refactoring task; may be deferred to a separate CR

---

### Phase 5: UI Code Changes — 5_Settings.py (Backup & Restore) — Risk: LOW

**Risk Assessment**: Low — mostly verification and a seed-script addition. Backup/restore is admin-only functionality.

**5.1 Verify Backup/Restore reflects new column names**
- [ ] Test `vault_export_full_backup` RPC returns data with `incubator_temp_f` (not `incubator_temp_c` or `ambient_temp`)
- [ ] Test `vault_admin_restore` (State 1 and State 2) inserts data correctly with new column names
- [ ] Test JSON Restore (`vault_restore_from_backup`) handles the new schema

**5.2 Add lookup table seed functionality**
- [ ] Create `supabase_db/migrations/v8_3_5_SEED_LOOKUP_TABLES.sql` with default rows for:
  ```sql
  -- Species
  INSERT INTO public.species (species_id, species_code, common_name, scientific_name, ...) VALUES
    ('BL', 'BL', 'Blanding''s Turtle', 'Emydoidea blandingii', ...),
    ('MK', 'MK', 'Common Musk Turtle (Stinkpot)', 'Sternotherus odoratus', ...)
  ON CONFLICT (species_id) DO NOTHING;
  
  -- Development Stages
  INSERT INTO public.development_stage (stage_id, label, description, ordinal_rank, sub_code) VALUES
    ('S0', 'Pre-Intake', 'Egg received but not yet assessed', 0, NULL),
    ('S1', 'Intake', 'Initial intake baseline established', 1, NULL),
    ('S2', 'Early Development', 'Spot, Band, or Full embryo visible', 2, 'Spot'),
    ('S2', 'Early Development', 'Spot, Band, or Full embryo visible', 2, 'Band'),
    ('S2', 'Early Development', 'Spot, Band, or Full embryo visible', 2, 'Full'),
    ...
  ON CONFLICT (stage_id) DO NOTHING;
  
  -- Biological Properties
  INSERT INTO public.biological_property (property_id, stage_id, property_label, data_type, is_critical) VALUES
    ('molding', 'S1', 'Molding', 'INTEGER_0_4', false),
    ('chalking', 'S2', 'Chalking', 'INTEGER_0_2', false),
    ...
  ON CONFLICT (property_id) DO NOTHING;
  ```
- [ ] Ensure State 1 (Clean Start) preserves and re-seeds these lookup tables

---

### Phase 6: PK/FK Standardization (Partial) — Risk: HIGH

**REVIEW NOTE — Risk Elevated**: The original plan's note about deferring the full UUID migration is correct, but adding `bin_code` and `egg_stage_code` as half-measures creates a transitional schema state with dual-purpose columns. Application code will need to handle BOTH `bin_id` (text) and `bin_code` (text) until full migration completes, which is error-prone.

**RECOMMENDATION**: Defer Phase 6 entirely to dedicated CR-20260501-PK-MIGRATION. If partial columns must be added now, add them as generated/computed columns that automatically mirror their source columns until the migration is complete.

**Risk Assessment**: High — partial PK migration leaves schema in transitional state; risk of application code using wrong column for joins; increased complexity with no immediate benefit until UUID migration completes.

**6.1 Add `bin_code` column** (IF DEFERRING: mark as DEFERRED — skip to Phase 7)
- [ ] **Migration**: `supabase_db/migrations/v8_4_1_ADD_BIN_CODE.sql`
  ```sql
  ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS bin_code text;
  UPDATE public.bin SET bin_code = bin_id;
  ```

**6.2 Add `egg_stage_code` column** (IF DEFERRING: mark as DEFERRED — skip to Phase 7)
- [ ] **Migration**: `supabase_db/migrations/v8_4_2_ADD_EGG_STAGE_CODE.sql`
  ```sql
  ALTER TABLE public.development_stage ADD COLUMN IF NOT EXISTS egg_stage_code text;
  UPDATE public.development_stage SET egg_stage_code = stage_id;
  ```

**6.3 Update application code references** (DEFERRED)
- [ ] All UI queries displaying bin identifiers: use `bin_code` instead of `bin_id`
- [ ] All UI queries displaying stage: use `egg_stage_code` instead of `stage_id`
- [ ] Foreign key columns in child tables will be migrated in a future CR (requires full data migration with UUID generation)

**Note**: The full PK migration to UUID is a MAJOR effort requiring coordinated changes across 5+ tables and all application code. Recommend deferring to a dedicated CR-20260501-PK-MIGRATION with its own testing cycle.

---

### Phase 7: Testing — Risk: MEDIUM

**REVIEW NOTE — Added tests for RPC layer**: Original Phase 8 had zero tests for the RPC functions despite Phase 2 being entirely RPC changes.

**Risk Assessment**: Medium — testing validates all prior changes. Risk is in missed regression scenarios, not in testing itself.

**7.1 Update existing tests**
- [ ] `tests/test_workflow_intake_save.py`: Update for new column names, removed mass/temp, new egg count logic
- [ ] `tests/test_workflow_observations_save.py`: Update for `incubator_temp_f`
- [ ] `tests/test_complex_multi_bin_workflow.py`: Update for supplemental mode changes
- [ ] `tests/test_db_state_management.py`: Verify backup/restore with new columns

**7.2 Add new test cases**
- [ ] `tests/test_supplemental_intake_workflow.py`: Test new bin to existing intake, test eggs to existing bin
- [ ] `tests/test_bin_config_grid.py`: Test current_egg_count read-only, new_egg_count editable
- [ ] `tests/test_intake_ui_labels.py`: Verify "Intake Date", "Egg Collection Method", radio options
- [ ] `tests/test_system_log_observer_id.py`: Verify audit logging works after migration
- [ ] ★NEW★ `tests/test_rpc_vault_finalize_intake.py`: Verify RPC accepts new payload format, rejects old format
- [ ] ★NEW★ `tests/test_rpc_vault_admin_restore.py`: Verify restore works with new column names
- [ ] ★NEW★ `tests/test_temp_column_migration.py`: Verify bin_observation temperature data survived migration

**7.3 End-to-end Playwright tests**
- [ ] `tests/e2e_playwright/test_intake_extended.py`: Update selectors for renamed labels
- [ ] `tests/e2e_playwright/test_observation_workflows.py`: Update for removed sidebar tools

---

### Phase 8: Documentation — Risk: LOW

**Risk Assessment**: Low — documentation-only, no system impact.

**8.1 Update requirements.md** (as identified in Gap Analysis §1.3)
**8.2 Update `docs/design/db_schema_export.txt`** with new schema
**8.3 Update `docs/user/OPERATOR_MANUAL.md`** for new UI labels and workflows
**8.4 Update `docs/BREADCRUMB_20260429.md`** with refactoring notes
**8.5 ★NEW★ Update `docs/deployment/rollback_procedures_CR-20260430-194500.md`** with validated rollback steps

---

### Phase 9: Deployment & Verification — Risk: MEDIUM

**Risk Assessment**: Medium — final integration and UAT. Risk is discovering integration issues late. Mitigated by the reordered phase dependencies ensuring schema changes deploy before UI changes.

**9.1 Pre-deployment checklist**
- [ ] All Phase 7 tests passing
- [ ] Rollback procedures validated in staging
- [ ] Database backup confirmed restorable
- [ ] Phase 0.4 audit findings documented and all migration scripts aligned with audit results

**9.2 Deploy migrations** via Supabase CI/CD pipeline
**9.3 Run full test suite**: `pytest tests/ -v --tb=short`
**9.4 Run end-to-end tests**: `bash scripts/run_e2e_tests.sh`
**9.5 Manual UAT**:
- New Intake with new labels
- Supplemental Intake with existing bin selection
- Observations with new temperature field name
- Backup & Restore both states
**9.6 Sign-off**: Update CR status to RESOLVED

---

## Summary of Estimated Effort (Revised)

| Phase | Description | LOE | Risk |
|-------|-------------|-----|------|
| Phase 0 | Preparation & Safeguards (+ pre-flight audit, rollback) | 2.5 hrs | LOW |
| Phase 1 | Schema & RPC Corrections (consolidated) | 4 hrs | MEDIUM |
| Phase 2 | Error Handling Fixes (reordered) | 1 hr | LOW |
| Phase 3 | UI Changes — 2_New_Intake.py | 4 hrs | MEDIUM |
| Phase 4 | UI Changes — 3_Observations.py | 2.5 hrs | MEDIUM |
| Phase 5 | UI Changes — 5_Settings.py | 1.5 hrs | LOW |
| Phase 6 | PK/FK Standardization (recommend DEFER) | 0 hrs (2 hrs if partial) | HIGH |
| Phase 7 | Testing (+ RPC tests) | 5 hrs | MEDIUM |
| Phase 8 | Documentation | 2 hrs | LOW |
| Phase 9 | Deployment & Verification | 2 hrs | MEDIUM |
| **Total** | | **~24.5 hours (LARGE)** | |

**If Phase 6 deferred**: ~22.5 hours.

---

## New Risks Identified (Review Addendum)

### R1: Streamlit Session State Staleness
After deploying UI changes (Phase 3-5), users with active Streamlit sessions may have stale session state variables from pre-deployment code. The radio button label change (3.2) is especially risky — `st.session_state` may hold the old string `"Supplemental Intake (Add to Existing Mother)"` after the code expects `"Add Eggs or Bins to Existing Intake"`. **Mitigation**: Add transitional handling in 3.2 that accepts both old and new strings, or force session reset via version bump.

### R2: Migration Application Order in CI/CD
If the CI/CD pipeline applies migrations sequentially and one fails mid-sequence (e.g., v8_3_2 fails after v8_3_0 succeeds), the RPCs will reference new column names but the schema columns won't match. **Mitigation**: Wrap Phase 1 migrations in a single transaction (`BEGIN; ... COMMIT;`) or use a single migration file.

### R3: `bin_observation` Temperature Data Loss
If Phase 0.4 audit shows data in `ambient_temp` (contrary to code analysis showing zero writes), and the migration in Phase 1.2a doesn't handle it, historical temperature readings will be lost. **Mitigation**: Phase 1.2a now includes a `COALESCE` migration for both source columns.

### R4: Foreign Key Constraint Violation on `system_log`
Phase 1.3 adds `system_log.observer_id` with a FK constraint to `observer`. If `system_log` has existing rows, and the insert tries to write an `observer_id` that doesn't exist in the `observer` table, the constraint will fail. **Mitigation**: Phase 2.1 already uses a try/except; additionally, consider making the FK `DEFERRABLE INITIALLY DEFERRED` or omitting the constraint initially.

### R5: Bin Code Display Before Full Migration
If Phase 6 is partially executed (adding `bin_code` column but not completing UUID migration), some application code will use `bin_code` for display while FK references still use `bin_id` (text). This dual-column state increases the likelihood of joining or displaying the wrong identifier. **Mitigation**: Defer Phase 6 entirely.
