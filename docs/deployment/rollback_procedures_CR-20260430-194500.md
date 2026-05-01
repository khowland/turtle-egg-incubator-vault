# Rollback Procedures for CR-20260430-194500

**Date:** 2026-05-01  
**Version:** 1.0  
**Status:** Ready for execution  

---

## Phase 1 Rollback (Schema & RPC)

### 1.1 Reverse renaming of bin_observation.ambient_temp → incubator_temp_f

**Migration file:** `v8_3_2`  
**What it does:** `ALTER TABLE public.bin_observation RENAME COLUMN ambient_temp TO incubator_temp_f;`

**Rollback SQL:**
```sql
ALTER TABLE public.bin_observation RENAME COLUMN incubator_temp_f TO ambient_temp;
```

**Notes:**
- No data loss risk: `bin_observation` has 0 rows as of preflight audit.
- No column was dropped; only renamed. Simple rename reversal.
- Execute this before reverting RPC changes, so old RPCs that reference `ambient_temp` will work again.

### 1.2 Reverse observer_id addition to system_log

**Migration file:** `v8_3_3`  
**What it does:** Adds `observer_id` column to `public.system_log`.

**Rollback SQL:**
```sql
ALTER TABLE public.system_log DROP COLUMN IF EXISTS observer_id;
```

**Notes:**
- Only drop if no dependent objects (views, functions) reference the column.
- If foreign key constraints were added, drop those first.

### 1.3 Reverse RPC function updates

**Migration file:** `v8_3_0`  
**What it does:** Updates RPC functions to use `incubator_temp_f` instead of `incubator_temp_c` and removes `incubator_temp_c` from `bin` INSERTs.

**Rollback options (choose one):**

**Option A – Deploy archived RPC files:**
```bash
# Deploy the pre-CR versions of affected RPCs
psql "$DATABASE_URL" -f supabase_db/archive/RPC_VAULT_FINALIZE_INTAKE.sql
psql "$DATABASE_URL" -f supabase_db/archive/v8_1_17_RPC_VAULT_EXPORT_BACKUP.sql
# Add any other RPC files that were modified by v8_3_0

> ⚠️ **CRITICAL**: RPC function rollback **requires** deploying the archived old RPC files. The pre-CR versions were archived to `supabase_db/archive/` during Phase 0. Without deploying the archived RPC files, the database functions will reference column names (`incubator_temp_f`) that no longer exist after schema rollback, causing application errors.

```

**Option B – Git revert the migration commit:**
```bash
git revert <commit-hash-for-v8_3_0>
# Push the revert and re-deploy Supabase functions
```

**Option C – Git checkout pre-CR tag (full revert of all Phase 1):**
```bash
git checkout tags/pre-CR-20260430-194500 -- supabase_db/
# Re-deploy all Supabase functions from that tag
```

**Verification:**
```sql
-- Confirm old function signature is restored
SELECT proname, prosrc FROM pg_proc WHERE proname = 'vault_finalize_intake';
-- Should NOT reference incubator_temp_f
```

---

## Phase 2 Rollback (Error Handling)

**Files changed:**
- `utils/bootstrap.py`
- `vault_views/2_New_Intake.py`

**Rollback:**
```bash
git revert <commit-hash-for-phase-2>
# Or if combined with other phases, revert specific files:
git checkout <pre-phase-2-commit> -- utils/bootstrap.py vault_views/2_New_Intake.py
git commit -m "Rollback Phase 2 error handling changes for CR-20260430-194500"
```

**Restart Streamlit after revert.**

---

## Phases 3-5 Rollback (UI Changes)

**Files changed:**
- `vault_views/2_New_Intake.py`
- `vault_views/3_Observations.py`
- `vault_views/5_Settings.py`

**Rollback:**
```bash
git revert <commit-hash-for-phases-3-5>
# Or file-specific checkout:
git checkout <pre-phase-3-commit> -- vault_views/2_New_Intake.py vault_views/3_Observations.py vault_views/5_Settings.py
git commit -m "Rollback Phases 3-5 UI changes for CR-20260430-194500"
```

**Restart Streamlit after revert.**

---

## Phase 6 Rollback (If Implemented – bin_code & egg_stage_code)

**Status:** Columns `bin_code` (on `bin`) and `egg_stage_code` (on `development_stage`) were added by this CR (migrations `v8_4_1` and `v8_4_2`). Use the rollback SQL below to reverse these additions.

**Rollback SQL:**
```sql
ALTER TABLE public.bin DROP COLUMN IF EXISTS bin_code;
ALTER TABLE public.development_stage DROP COLUMN IF EXISTS egg_stage_code;
```

**Notes:**
- If any constraints, indexes, or views depend on these columns, drop those dependencies first.
- If the columns were used to replace existing columns (e.g., `bin_id` → `bin_code` as PK), this rollback is more complex and requires data migration reversal. Refer to the full system rollback procedure below.

---

## Full System Rollback (Nuclear Option)

Use this if multiple phases need to be rolled back simultaneously or if a phased rollback fails.

### Step 1: Restore database backup
```bash
# Restore from pre-CR backup
psql "$DATABASE_URL" < /a0/usr/workdir/backups/cr194500/turtledb_backup_<timestamp>.sql

# Or use the JSON exports to rebuild tables if SQL dump unavailable
# (JSON exports are at /a0/usr/workdir/backups/cr194500/)
```

### Step 2: Revert codebase
```bash
# Option A: Checkout the pre-CR tag
git checkout tags/pre-CR-20260430-194500

# Option B: Hard reset to the commit before CR started
git reset --hard <commit-before-cr-20260430-194500>
```

### Step 3: Restart services
```bash
# Re-deploy Supabase functions if using CLI
supabase functions deploy

# Restart Streamlit application
pkill -f streamlit
streamlit run app.py &
```

### Step 4: Verify
```sql
-- Confirm schema is back to pre-CR state
SELECT column_name FROM information_schema.columns WHERE table_name = 'bin_observation';
-- Should show 'ambient_temp', NOT 'incubator_temp_f'

SELECT column_name FROM information_schema.columns WHERE table_name = 'system_log';
-- Should NOT include 'observer_id'
```

---

## Rollback Decision Matrix

| Failure Scenario | Recommended Rollback |
|------------------|---------------------|
| Rename column fails mid-migration | Execute Phase 1.1 rollback |
| RPC errors after deploy | Execute Phase 1.3 Option A (redeploy old RPCs) |
| UI breaks after Phase 3-5 deploy | Execute Phases 3-5 rollback (git revert) |
| Multiple phases fail | Full System Rollback (restore DB + git checkout) |
| Data corruption detected | Full System Rollback |

---

*Document generated as part of CR-20260430-194500 Phase 0.5*
