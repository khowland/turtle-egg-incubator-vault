# Implementation Plan for CR-20260430-194500

**Data Architecture Integrity & System Refactoring**

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

**Gap Assessment**:
| Item | Required by Expert | In requirements.md | In System | Gap |
|------|-------------------|-------------------|-----------|-----|
| Molding (0-4) | Yes | No | Hardcoded (0-2) | Range mismatch; should be 0-4 per expert but hardcoded at 0-2. |
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

**Rationale**: incubator_temp_c was incorrectly placed on `bin` table and used Celsius naming despite storing Fahrenheit values. It belongs on `bin_observation` as a per-session reading.

**Current references — all files that MUST be updated**:

| File | Line(s) | Current Reference | Action |
|------|---------|-------------------|--------|
| `supabase_db/migrations/RPC_VAULT_FINALIZE_INTAKE.sql` | 105,117,132,142 | `incubator_temp_c` in INSERT statements | Remove from INT/INSERT into `bin` table. RPC should no longer accept this field for bin creation. |
| `supabase_db/migrations/v8_1_16_ADD_TEMP_TO_BIN_OBS.sql` | 10,13 | `ALTER TABLE ... ADD COLUMN incubator_temp_c` | **Reverse**: Drop column from `bin`, keep on `bin_observation` but rename to `incubator_temp_f` |
| `supabase_db/migrations/v8_1_18_RPC_VAULT_ADMIN_RESTORE.sql` | 47,58 | `incubator_temp_c` in INSERT | Replace with `NULL` for `bin` table inserts |
| `supabase_db/migrations/v8_1_19_ENFORCE_TIMESTAMP_SOVEREIGNTY.sql` | 85,88,94,98 | `incubator_temp_c` references | Replace all → `incubator_temp_f` on bin_observation; remove from bin INSERT |
| `supabase_db/migrations/v8_1_21_ADD_DAYS_IN_CARE.sql` | 83,86,92,96 | Same pattern | Same fix |
| `supabase_db/migrations/v8_1_22_MOTHER_WEIGHT.sql` | 83,86,92,96 | Same pattern | Same fix |
| `supabase_db/migrations/v8_1_25_SUPPLEMENTAL_INTAKE.sql` | 64,73 | `incubator_temp_c` references | Same fix |
| `supabase_db/migrations/v8_1_27_RPC_VAULT_ADMIN_RESTORE_V2.sql` | 110,126,174,188,229,243 | Multiple references | Same fix |
| `vault_views/2_New_Intake.py` | 289 | `"incubator_temp_c": row_data["temp"]` in bins_payload | **Remove entirely** — no longer sent in intake RPC |
| `vault_views/3_Observations.py` | ~700-900 (observation saving) | References `ambient_temp` in bin_observation insert | Rename to `incubator_temp_f` |
| `vault_views/5_Settings.py` | Backup/Restore section (lines 429-542) | Calls `vault_admin_restore` and `vault_export_full_backup` | Verify restored data uses new column names |
| `scripts/` | `forensic_auditor.py`, `seed_complex_scenario.py`, `backend_qa_verification.py` | May reference old columns | Audit and update |
| `tests/` | Multiple test files with SQL verification | May reference `incubator_temp_c` or `ambient_temp` | Update all test assertions |

### 2.2 `ambient_temp` → `incubator_temp_f` (bin_observation table)

**Current references**:
| File | Location | Current Reference | Action |
|------|----------|-------------------|--------|
| `supabase_db/turtledb_schema_generated_04282026.txt` | Line 39 | `ambient_temp numeric` on bin_observation | Column rename |
| Migration files | All RPCs that insert into bin_observation | `ambient_temp` parameter | Rename |
| `vault_views/3_Observations.py` | Observation saving logic | `ambient_temp` in insert payload | Rename to `incubator_temp_f` |

### 2.3 `bin.bin_id` → `bin.bin_code` (new column) + PK migration

**Current state**: `bin.bin_id` is a `text` column storing system-generated bin codes (e.g., "BL1-HOWLAND-1") AND serving as the primary key. It is referenced as a foreign key in `egg`, `bin_observation`, and `egg_observation`.

**Required change**:
1. Add new `bin_code text` column to `bin`
2. Copy existing values: `UPDATE bin SET bin_code = bin_id`
3. Add new `bin_id uuid` column with auto-generated UUIDs
4. Update all FK references across `egg`, `bin_observation`, `egg_observation`
5. Eventually drop the old text PK and promote the UUID column

**Impact — files referencing `bin.bin_id`**:

| File | Usage | Action |
|------|-------|--------|
| `vault_views/1_Dashboard.py` | Queries bin_id for display and workbench | Update to use `bin_code` for display, `bin_id` (new UUID) for joins |
| `vault_views/2_New_Intake.py` | Generates bin codes, inserts via RPC | Update RPC to accept `bin_code`, let DB generate `bin_id` UUID |
| `vault_views/3_Observations.py` | Queries by bin_id, inserts observations | Replace `bin_id` references with new UUID column for FK; use `bin_code` for display |
| `vault_views/6_Reports.py` | Analytics queries | Update queries |
| `vault_views/7_Diagnostic.py` | Diagnostic queries | Update queries |
| `utils/bootstrap.py` | `get_last_bin_weight()` queries by bin_id | Update FK column name |
| All migration RPC files | INSERT/UPDATE on bin, egg, *_observation | Add `bin_code` handling; use new UUID `bin_id` |
| All test files | SQL verification queries | Update column references |
| `scripts/forensic_auditor.py` | Audit queries | Update |

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

## Part 3: Merged Implementation Plan

This plan incorporates all actionable items from CR-20260430-181500 (except the rejected Section 1.1) and the new requirements from CR-20260430-194500. Each phase contains detailed, atomic tasks suitable for delegation to lower-level agents.

---

### Phase 0: Preparation & Safeguards

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

---

### Phase 1: Schema Corrections (Temperature Columns)

**1.1 Drop `incubator_temp_c` from `bin` table**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_1_DROP_INCUBATOR_TEMP_FROM_BIN.sql`
  ```sql
  ALTER TABLE public.bin DROP COLUMN IF EXISTS incubator_temp_c;
  ```
- [ ] Deploy via CI/CD pipeline. Verify with: `SELECT column_name FROM information_schema.columns WHERE table_name = 'bin' AND column_name = 'incubator_temp_c';` — must return 0 rows.

**1.2 Rename `bin_observation.ambient_temp` → `bin_observation.incubator_temp_f`**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_2_RENAME_AMBIENT_TEMP_TO_INCUBATOR_TEMP_F.sql`
  ```sql
  ALTER TABLE public.bin_observation RENAME COLUMN ambient_temp TO incubator_temp_f;
  ```
- [ ] Verify: `SELECT column_name FROM information_schema.columns WHERE table_name = 'bin_observation' AND column_name = 'incubator_temp_f';` — must return 1 row.
- [ ] Keep `incubator_temp_c` on `bin_observation` for now (rename later if needed, but CR says to use `incubator_temp_f`). If both exist, consolidate.

**1.3 Add `observer_id` column to `system_log`**
- [ ] **Migration file**: `supabase_db/migrations/v8_3_3_ADD_OBSERVER_ID_TO_SYSTEM_LOG.sql`
  ```sql
  ALTER TABLE public.system_log ADD COLUMN IF NOT EXISTS observer_id uuid;
  ALTER TABLE public.system_log ADD CONSTRAINT system_log_observer_id_fkey
      FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);
  ```
- [ ] This fixes the `PGRST204` error when `safe_db_execute` inserts audit records.

---

### Phase 2: Update All RPC Functions

**2.1 Update `vault_finalize_intake` to remove `incubator_temp_c` from bin INSERT**
- [ ] Edit latest RPC file (currently `v8_1_25_SUPPLEMENTAL_INTAKE.sql` or create new `v8_3_4_UPDATE_RPC_VAULT_FINALIZE_INTAKE.sql`)
- [ ] Remove `incubator_temp_c` from the `INSERT INTO public.bin (...)` column list
- [ ] Remove `(v_bin->>'incubator_temp_c')::numeric` from VALUES clause
- [ ] Remove `incubator_temp_c` from `bin_observation` INSERT (replaced by `incubator_temp_f` in Phase 3)
- [ ] Test via Supabase SQL Editor: `SELECT vault_finalize_intake('{"species_id":"BL","next_intake_number":1,...}');`

**2.2 Update `vault_admin_restore` and `vault_export_full_backup`**
- [ ] Replace all `incubator_temp_c` references with `incubator_temp_f` on bin_observation
- [ ] Remove `incubator_temp_c` from bin table operations
- [ ] Ensure backup/restore handles the new column names

**2.3 Archive old RPC versions**
- [ ] Move `RPC_VAULT_FINALIZE_INTAKE.sql`, `v8_1_16_ADD_TEMP_TO_BIN_OBS.sql`, `v8_1_18_RPC_VAULT_ADMIN_RESTORE.sql`, `v8_1_19_ENFORCE_TIMESTAMP_SOVEREIGNTY.sql`, `v8_1_21_ADD_DAYS_IN_CARE.sql`, `v8_1_22_MOTHER_WEIGHT.sql`, `v8_1_25_SUPPLEMENTAL_INTAKE.sql` to `supabase_db/archive/`
- [ ] Keep only the latest consolidated versions

---

### Phase 3: UI Code Changes — 2_New_Intake.py

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

**3.3 Remove `incubator_temp_c` from bins_payload**
- [ ] **Line 289**: Delete `"incubator_temp_c": row_data["temp"]` from the bins_payload dictionary
- [ ] Remove `"bin_weight_g": row_data["mass"]` as well (mass moved to Observations per CR-20260430-181500)

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

### Phase 4: UI Code Changes — 3_Observations.py

**4.1 Rename `ambient_temp` → `incubator_temp_f` in observation inserts**
- [ ] Search and replace all instances of `"ambient_temp"` with `"incubator_temp_f"` in bin_observation INSERT payloads
- [ ] Update column labels in the UI from "Ambient Temp" to "Incubator Temp (°F)"

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

### Phase 5: UI Code Changes — 5_Settings.py (Backup & Restore)

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

### Phase 6: Error Handling Fixes

**6.1 Fix `safe_db_execute` dual error insertion**
- [ ] **File**: `utils/bootstrap.py`, lines 346-410
- [ ] In the `except` block (line 375+), remove the second `system_log.insert()` attempt that references `observer_id` before the column exists
- [ ] Or better: add a try/except around the system_log insert to silently fail if column missing
```python
try:
    get_resilient_table(get_supabase(), "system_log").insert({
        "session_id": st.session_state.get("session_id", "SYSTEM"),
        "event_type": "ERROR",
        "event_message": f"{operation_name} failed: {str(e)}",
    }).execute()
except Exception:
    pass  # system_log may not have observer_id column yet
```

**6.2 Fix `commit_all` inner exception handler**
- [ ] **File**: `vault_views/2_New_Intake.py`, lines 353-362
- [ ] Remove `observer_id` from the system_log insert, or add conditional:
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

**6.3 Fix dual error propagation**
- [ ] The inner `except` in commit_all raises after logging, which triggers the outer `except` in `safe_db_execute`, which logs again and re-raises. This doubles the error display.
- [ ] Solution: Either remove the outer `safe_db_execute` wrapper (since commit_all already has its own error handling), or remove the inner re-raise.

---

### Phase 7: PK/FK Standardization

**7.1 Add `bin_code` column**
- [ ] **Migration**: `supabase_db/migrations/v8_4_1_ADD_BIN_CODE.sql`
  ```sql
  ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS bin_code text;
  UPDATE public.bin SET bin_code = bin_id;
  ```

**7.2 Add `egg_stage_code` column**
- [ ] **Migration**: `supabase_db/migrations/v8_4_2_ADD_EGG_STAGE_CODE.sql`
  ```sql
  ALTER TABLE public.development_stage ADD COLUMN IF NOT EXISTS egg_stage_code text;
  UPDATE public.development_stage SET egg_stage_code = stage_id;
  ```

**7.3 Update application code references**
- [ ] All UI queries displaying bin identifiers: use `bin_code` instead of `bin_id`
- [ ] All UI queries displaying stage: use `egg_stage_code` instead of `stage_id`
- [ ] Foreign key columns in child tables will be migrated in a future CR (requires full data migration with UUID generation)

**Note**: The full PK migration to UUID is a MAJOR effort requiring coordinated changes across 5+ tables and all application code. Recommend deferring to a dedicated CR-20260501-PK-MIGRATION with its own testing cycle.

---

### Phase 8: Testing

**8.1 Update existing tests**
- [ ] `tests/test_workflow_intake_save.py`: Update for new column names, removed mass/temp, new egg count logic
- [ ] `tests/test_workflow_observations_save.py`: Update for `incubator_temp_f`
- [ ] `tests/test_complex_multi_bin_workflow.py`: Update for supplemental mode changes
- [ ] `tests/test_db_state_management.py`: Verify backup/restore with new columns

**8.2 Add new test cases**
- [ ] `tests/test_supplemental_intake_workflow.py`: Test new bin to existing intake, test eggs to existing bin
- [ ] `tests/test_bin_config_grid.py`: Test current_egg_count read-only, new_egg_count editable
- [ ] `tests/test_intake_ui_labels.py`: Verify "Intake Date", "Egg Collection Method", radio options
- [ ] `tests/test_system_log_observer_id.py`: Verify audit logging works after migration

**8.3 End-to-end Playwright tests**
- [ ] `tests/e2e_playwright/test_intake_extended.py`: Update selectors for renamed labels
- [ ] `tests/e2e_playwright/test_observation_workflows.py`: Update for removed sidebar tools

---

### Phase 9: Documentation

**9.1 Update requirements.md** (as identified in Gap Analysis §1.3)
**9.2 Update `docs/design/db_schema_export.txt`** with new schema
**9.3 Update `docs/user/OPERATOR_MANUAL.md`** for new UI labels and workflows
**9.4 Update `docs/BREADCRUMB_20260429.md`** with refactoring notes

---

### Phase 10: Deployment & Verification

**10.1 Deploy migrations** via Supabase CI/CD pipeline
**10.2 Run full test suite**: `pytest tests/ -v --tb=short`
**10.3 Run end-to-end tests**: `bash scripts/run_e2e_tests.sh`
**10.4 Manual UAT**:
- New Intake with new labels
- Supplemental Intake with existing bin selection
- Observations with new temperature field name
- Backup & Restore both states
**10.5 Sign-off**: Update CR status to RESOLVED

---

## Summary of Estimated Effort

| Phase | Description | LOE |
|-------|-------------|-----|
| Phase 0 | Preparation & Safeguards | 1 hr |
| Phase 1 | Schema Corrections (Temp Columns) | 1 hr |
| Phase 2 | Update All RPC Functions | 3 hrs |
| Phase 3 | UI Changes — 2_New_Intake.py | 4 hrs |
| Phase 4 | UI Changes — 3_Observations.py | 2 hrs |
| Phase 5 | UI Changes — 5_Settings.py | 1.5 hrs |
| Phase 6 | Error Handling Fixes | 1 hr |
| Phase 7 | PK/FK Standardization | 2 hrs |
| Phase 8 | Testing | 4 hrs |
| Phase 9 | Documentation | 2 hrs |
| Phase 10 | Deployment & Verification | 1.5 hrs |
| **Total** | | **~23 hours (LARGE)** |
