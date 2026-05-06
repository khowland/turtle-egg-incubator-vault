# 🍞 BREADCRUMB — Session State for Next Chat

**Date:** 2026-05-06 00:17 CT  
**Version:** v9.2.0 WINC Incubator  
**Chat Context:** Heavily loaded — this is the fresh-chat handoff

---

## 📊 CURRENT QA TRIAD STATUS

| Task ID | File | Status | Strike Count | Notes |
| :--- | :--- | :--- | :--- | :--- |
| TSK-01 | `TEST_MATRIX_SETTINGS.md` | `[GREEN_COMPLETED]` | 0 | Documentation artifact. 18 test cases |
| TSK-02 | `TEST_MATRIX_REPORTS.md` | `[GREEN_COMPLETED]` | 0 | Documentation artifact. 14 test cases |
| TSK-05 | `test_adversarial_intake.py` | `[GREEN_COMPLETED]` | 0 | 7/7 adversarial tests passed |
| **TSK-03** | `test_intake_extended.py` | `[READY_TO_RUN]` | 0 (reset) | Already uses `input[aria-label='New Eggs']` selector. 4 tests. |
| **TSK-04** | `test_observation_workflows.py` | `[READY_TO_RUN]` | **Strike 2** (ENV_BLOCK, NOT HARD_LOCK) | 7 tests. Red team ruled infrastructure failure doesn't count as test regression strike. |
| **TSK-06** | `test_adversarial_observations.py` | `[NEEDS_VALIDATION]` | 0 | Written: 4 adversarial stage jump tests. Needs sub-agent Validator review. |
| **TSK-07** | `test_phase5_scalability_loop.py` | `[READY_TO_RUN]` | 0 | 1 test: 50x observation loop with DB Pincer audit. |
| TSK-08 | `test_adversarial_input.py` | `[NEEDS_VALIDATION]` | 0 | Written: 3 adversarial input tests (SQLi, XSS, empty fields). Needs Validator. |

---

## ✅ COMPLETED THIS SESSION (2026-05-05)

### Schema Fixes (Applied by Kevin)
- `ALTER TABLE bin_observation ADD COLUMN observer_id uuid;` — CR-P0-01
- `ALTER TABLE session_log ADD COLUMN modified_at timestamptz;` — CR-P0-02
- `ALTER TABLE bin_observation ADD COLUMN created_at timestamptz;` — CR-P1-02
- `ALTER TABLE egg_observation ADD COLUMN created_at timestamptz;` — CR-P1-02
- `ALTER TABLE bin_observation ADD COLUMN obs_id text;` — Fix for RPC `record "new" has no field "obs_id"`

### CRs Implemented (Code Changes)
- **CR-P1-01:** Replaced supplemental `st.data_editor` with per-row `st.number_input` in `vault_views/2_New_Intake.py` (lines ~280-310)
- **CR-P2-01:** Stage jump validator: `st.error` + `st.stop()` enforcement in `vault_views/3_Observations.py` (lines 546-558)
- **CR-P2-02:** `bin_code` display leaks — Settings line 336 already fixed; Reports export updated
- **CR-P2-03:** RPC migration column drift — verified, no code change needed
- **CR-P3-01:** `@st.cache_data(ttl=300)` on species list and `get_app_version()` cache
- **Cat-A:** Shared helper cascade — `_create_intake_and_get_bin()` updated from dvn-cell to `input[aria-label='New Eggs']` in `test_bin_environment.py` lines 76-80
- **Cat-D:** Navigation timing — SAVE wait 2000→500 ms in `test_bin_environment.py` lines 84-87

### Documentation
- `QA_TRIAD_LEDGER.md` updated: TSK-03, TSK-06 reopened; TSK-08 added
- `tests/resolved_bugs/00_CENTRAL_HUB.md` updated: 9 completed CR entries added
- `BUG-SCHEMA-001_004_resolution.md` created documenting schema migration gaps

### Conftest Fix
- `tests/e2e_playwright/conftest.py` line 61: replaced hardcoded `.neq('id', 0)` with table-specific PK column name map (`intake_id`, `bin_id`, `egg_id`, etc.)

---

## 🔴 BLOCKER: START Button Timeout (All 12 Tests)

**Symptom:** Every test in TSK-03, TSK-04, TSK-07 fails with:
```
playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log: waiting for get_by_role("button", name="START", exact=True)
```

**Root Cause (Red Team Analysis):** The Streamlit app is in an error state from stale session + schema drift. Instead of rendering the login page with the START button, it renders Streamlit's generic error page because `vault_finalize_intake` RPC fails when encountering missing columns (`obs_id`, previously `observer_id`).

**After schema fixes applied (including obs_id):** The app needs a RESTART to clear the stale session state. The `obs_id` column was the last missing piece.

**Fix:**
```bash
pkill -f streamlit
streamlit run app.py --server.port 8599 --server.headless true
```
Then re-run TSK-03, TSK-04, TSK-07.

---

## 🔑 CRITICAL ENVIRONMENT NOTES

- **App URL:** `http://127.0.0.1:8599`
- **Supabase:** Live production (kxfkfeuhkdopgmkpdimo.supabase.co)
- **Schema reference:** `supabase_db/turtledb_schema_generated_20260505.txt` (fresh from Supabase)
- **All schema fixes applied** — verify with schema dump that `obs_id`, `observer_id`, `created_at`, `modified_at` columns exist
- **Login:** START button on splash page — selector: `page.get_by_role("button", name="START", exact=True)`
- **User:** Kevin Howland
- **Python venv:** `/opt/venv/bin/python`
- **Streamlit cache:** `@st.cache_data(ttl=300)` on species list and APP_VERSION — may need cache clearing after schema changes

---

## 🚀 IMMEDIATE NEXT STEPS (In Order)

1. **Restart Streamlit app** — clear stale session, verify login page renders
2. **Run TSK-07** (Strike 0, lowest risk) — `pytest tests/e2e_playwright/test_phase5_scalability_loop.py -v --tb=short`
3. **Run TSK-03** (Strike 0) — `pytest tests/e2e_playwright/test_intake_extended.py -v --tb=short`
4. **Run TSK-04** (Strike 2, careful) — `pytest tests/e2e_playwright/test_observation_workflows.py -v --tb=short`
5. **Validator review TSK-06 and TSK-08** — submit to developer sub-agent for static analysis
6. **Update QA_TRIAD_LEDGER.md** with results and commit
7. **Fix login fixture resilience** — add error page detection per red team recommendation (conftest.py)

---

## ⚠️ TSK-04 Strike 2 NOTE

**Do NOT hard-lock TSK-04.** The START button timeout is an infrastructure failure (app error state), not a test logic regression. Red team ruled it as `ENV_BLOCK`. If it fails on re-run with app healthy, then it counts toward Strike 3. If it passes, reset to Strike 0.

---

## 📁 KEY FILES FOR NEXT AGENT TO READ FIRST

1. `tests/QA_TRIAD_LEDGER.md` — authoritative task status
2. `tests/resolved_bugs/00_CENTRAL_HUB.md` — resolved bugs registry
3. `docs/implied_system_objective.md` — system requirements
4. `docs/e2e_failure_analysis_v920.md` — comprehensive failure analysis
5. `BREADCRUMB.md` — this file

---

## 🔗 PROMPTINCLUDE FILES (Auto-Injected)

- `claude.promptinclude.md` — Engineering & QA Methodology
- `qa.promptinclude.md` — QA Methodology (KB-First, Mandatory Reporting, etc.)
- `subagent.promptinclude.md` — Sub-Agent & Skills Orchestration

These are automatically loaded into the system prompt. No need to re-read them.
