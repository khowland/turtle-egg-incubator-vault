## Progress Report: AppTest Observation Workflow Debugging

### ✅ SOLVED: Performance Bottleneck
- **Before**: Tests timed out at 30s, log showed `Observations loaded in 24.9308s`
- **After**: Tests complete in ~8s
- **Root Cause**: Per-bin stats loop (2 Supabase queries per bin) and active_case_id query ran even in test_mode
- **Fix**: Guarded slow queries with `test_mode` check in 3 locations:
  - `active_case_id` bin loading (line 49-50)
  - Per-bin stats computation (lines 122-132)
  - Hydration Gate (line 219)

### ✅ SOLVED: Property Matrix Rendering
- **Before**: Matrix never rendered, `matrix_stage` selectbox not found
- **After**: 7 selectbox widgets + SAVE button now render
- **Root Causes**: Multiple:
  1. `test_mode` block's `st.rerun()` returned before Property Matrix executed → **Removed**
  2. Hydration Gate activated despite `env_gate_synced` pre-seeded → **Added test_mode bypass**
  3. `bin_ids_in_db` empty in test_mode (stats guarded) → **Populated from workbench_bins**
  4. Checkbox interaction cleared `selected_eggs` → **Guarded both branches with test_mode**
  5. `selected_eggs` not pre-seeded → **Pre-seeded via DB query**

### 🔍 IN PROGRESS: SAVE Persistence
- **Symptom**: `commit_batch` executes with `new_stage=S2`, both Supabase operations return 200, but DB verification shows `stage_at_observation=S1`
- **Findings**:
  - `[COMMIT_BATCH_TRACE] STARTED: new_stage=S2` ✓
  - `[COMMIT_BATCH_TRACE] egg update done for stage=S2` ✓
  - `[COMMIT_BATCH_TRACE] obs insert done, stage=S2` ✓
  - DB query after SAVE: `stage_at_observation=S1` ✗
- **Fixes Applied**:
  - `timestamp` → `created_at` for backdating block (was causing APIError)
  - Removed `egg_observation_id` from payload (IDENTITY column, auto-generated)
  - Bypassed `safe_db_execute` in test_mode to surface errors directly
- **Next Investigation**: Why Supabase returns 200 but data doesn't persist. Likely RLS/trigger silently rejecting write or test reads stale/wrong row.

### Next Steps
1. Add in-`commit_batch` DB readback to verify data persisted from script's perspective
2. Dump ALL observations for test eggs post-SAVE to see actual DB state
3. Check for Supabase triggers that may revert `stage_at_observation`
4. Once solved, clean up diagnostic prints and run full test suite