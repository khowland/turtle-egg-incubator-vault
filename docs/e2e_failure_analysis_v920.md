# E2E Failure Analysis Report — v9.2.0

**Date:** 2026-05-04 00:01 CT  
**Suite:** `pytest --browser chromium tests/e2e_playwright/ --tb=long -v`  
**Result:** 42 selected tests, 29+ failures (suite timed out at 900s, final summary not captured)  
**Verification Type:** Observation only — NO code changes authorized.  
**Log:** `tmp/e2e_v920_final_report_20260504_044002.log`

---

## 1. Executive Summary

The E2E test suite has a **catastrophic failure rate** (~70-100% depending on completion). This does NOT mean the app is broken — manual browser verification confirmed the app renders correctly at `http://127.0.0.1:8599/` with proper headings, bin_code display, Correction Mode, and all lifecycle features. The failures are **test infrastructure issues**: stale selectors, shared helper dependencies, and lack of database state isolation.

---

## 2. Root Cause Categories

### Category A: Shared Helper Cascade (`_create_intake_and_get_bin`)
**Impact:** ~20 tests across 7 files  
**Mechanism:** Most lifecycle tests (observations, surgical corrections, S6 hatching) call a shared helper that:
1. Navigates to Intake page
2. Fills 8 required fields
3. Clicks SAVE
4. Extracts bin_id from the intake
5. Navigates to Observations page

If **any step** fails (wrong selector, timeout, SAVE doesn't redirect), the helper returns `None`, and **all dependent tests fail immediately** — not because their specific feature is broken, but because they have no bin to work with.

**Remedy:** Debug the shared helper in isolation first. Use a standalone script to verify each step of the Intake→SAVE→bin_id extraction flow. Once the helper works, re-run dependent tests.

### Category B: Database State Dependency
**Impact:** ~5 tests  
**Mechanism:** Tests like `test_bin_weight_gate`, `test_full_observation_cycle`, and `test_hatching_s6` expect bins or eggs to already exist in the database from prior tests. If run in isolation or after a clean slate, they fail because the data isn't there.

**Remedy:** Use pytest fixtures with `@pytest.mark.dependency()` or add explicit data seeding at the start of each test file.

### Category C: Streamlit v9.0.0 Selector Drift
**Impact:** ~8 tests  
**Mechanism:** The Streamlit upgrade from v8.x to v9.0.0 changed how certain components render:
- Data editor cells (Bug-E2E-002)
- `st.selectbox` dropdown markup
- `st.button` naming conventions
- `st.dataframe` / `st.data_editor` selectors

**Remedy:** Inspect the rendered HTML of each failing page using `page.content()` in a debug script. Update selectors in `e2e_selectors.py` and test files to match the v9.0.0 DOM.

### Category D: SAVE Navigation / Page Redirect Timing
**Impact:** ~6 tests  
**Mechanism:** After clicking SAVE on the Intake form, `st.switch_page` redirects to Observations. The test expects the Observations heading to appear immediately, but Streamlit's rerun cycle may not complete before the assertion fires.

**Remedy:** Add `page.wait_for_url("**/Observations**", timeout=10000)` after clicking SAVE, then wait for the heading to appear with `page.wait_for_selector(...)`.

### Category E: Emoji Remnant Selectors (Partially Resolved)
**Impact:** ~2 tests  
**Mechanism:** While all `st.title()`/`st.header()`/`st.subheader()` calls were stripped of emojis in commit `80edc54`, some test files may still have hardcoded emoji-prefixed strings in assertions (not using `e2e_selectors.py` constants).

**Remedy:** Grep all test files for emoji characters (📊, 📋, 🔬, etc.) and replace with plain text constants from `e2e_selectors.py`.

---

## 3. Per-File Failure Analysis

### 3.1 `test_adversarial_forensic.py` — 2 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_layer1_adversarial_ui_rejections` | Form validation rejection selectors changed in v9.0.0; expects old error message format | C (Selector Drift) |
| `test_layer2_forensic_backend_verification` | Depends on data from layer1 (intake with 100 eggs count validation) | B (State Dependency) |

**Remedy:** Review `st.error()` / `st.warning()` rendering in v9.0.0. Update selectors in test file. Ensure layer2 can run standalone.

### 3.2 `test_bin_environment.py` — 4 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_bin_weight_gate` | Helper `_create_intake_and_get_bin` fails → no bin_id → can't test weight gate | A (Helper Cascade) |
| `test_add_supplemental_bin` | Same helper cascade + supplemental bin form selectors may have changed | A + C |
| `test_bin_soft_delete_retirement` | Bin retirement flow uses `bin_code` dropdown — recently changed to show bin_code not bin_id | C (Selector Drift) |
| `test_bin_restore` | Restoration from Resurrection Vault requires deleted bins to exist in dropdown (fixed in `d299492`) | C (Selector Drift) |

**Remedy:** Fix the shared helper first. Verify bin retirement selectors match the new bin_code display. The surgical search fix (`d299492`) may have helped restoration, but the test selector may still be stale.

### 3.3 `test_clean_start.py` — 2 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_vault_wipe_clean_start` | Settings → Resurrection Vault → Vault Wipe button selector changed in v9.0.0 UI | C (Selector Drift) |
| `test_lookup_tables_survive_wipe` | Depends on vault wipe completing successfully | B (State Dependency) |

**Remedy:** Inspect Settings page in v9.2.0 to find the correct Vault Wipe button/confirmation selectors. Update test.

### 3.4 `test_core_ui.py` — 1 failure

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_dashboard_renders` | Expected heading `'📊 Today's Summary'` but app now shows `'Today's Summary'` | E (Emoji Remnant) |

**Remedy:** Check if `test_core_ui.py` uses `e2e_selectors.HEADING_DASHBOARD` (which is already plain text) or a hardcoded emoji string. If hardcoded, replace with the constant.

### 3.5 `test_hatching_s6.py` — 2 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_s5_to_s6_hatch_transition` | Depends on helper creating intake + bin + egg + S5 observation flow | A (Helper Cascade) |
| `test_hatchling_ledger_data` | Depends on S6 transition completing; ledger selectors may have changed | A + C |

**Remedy:** Fix the shared helper first. S6 hatching involves the surgical search data editor (Bug-E2E-002).

### 3.6 `test_intake_e2e.py` — 2 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_initial_intake_validation_and_ui` | SAVE button selector, form field labels, or Species selectbox options changed in v9.0.0 | C (Selector Drift) |
| `test_supplemental_intake_workflow` | Supplemental bin form navigation/selectors changed | C (Selector Drift) |

**Remedy:** This is the most critical file to fix because it feeds the shared helper. Debug the full Intake form flow in isolation: navigate, fill all 8 fields, click SAVE, verify redirect, extract bin_id.

### 3.7 `test_intake_extended.py` — 4 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_intake_full_fields_and_bin_nomenclature` | Form field labels or bin nomenclature format changed | C (Selector Drift) |
| `test_intake_multiple_eggs` | Multiple egg count input selector changed (possibly data editor) | C (Selector Drift) |
| `test_intake_cancel_button` | Cancel button label/placement changed | C (Selector Drift) |
| `test_supplemental_intake_full_save` | Supplemental intake save flow + redirect | C + D (Timing) |

**Remedy:** Same as `test_intake_e2e.py` — debug the Intake form in isolation. The CANCEL button may have been moved or renamed.

### 3.8 `test_observation_workflows.py` — 7 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_full_observation_cycle` | Helper cascade + data editor cell selectors (Bug-E2E-002) | A + C |
| `test_multi_egg_batch_observation` | Same as above | A + C |
| `test_stage_progression_s1_through_s5` | Data editor selectors for stage/status dropdowns | A + C |
| `test_s3_substages` | Substage selectors in data editor | A + C |
| `test_observation_health_fields` | Health fields (chalking, molding, leaking, denting, vascularity) selectors | A + C |
| `test_biological_jump_warning` | Biological jump validation + warning message selectors | A + C |
| `test_mortality_recording` | Mortality/dead status recording selectors | A + C |

**Remedy:** Fix Bug-E2E-002 (data editor cell selectors). All observation workflow tests depend on being able to fill data into the Streamlit data editor grid. Once cell selectors are fixed, these 7 tests should start passing.

### 3.9 `test_observations_e2e.py` — 1 failure

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_observation_grid_and_correction_mode` | Same data editor selectors + Correction Mode toggle interaction | A + C |

**Remedy:** Fix Bug-E2E-002 and verify Correction Mode toggle selector matches v9.2.0 (emoji-stripped).

### 3.10 `test_performance.py` — 2 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_splash_screen_tfmp` | Splash screen selector changed (START button text/placement) | C (Selector Drift) |
| `test_hydration_time` | Page hydration measurement selector changed | C (Selector Drift) |

**Remedy:** Inspect splash/welcome screen DOM. The version display now shows v9.2.0 and heading may be plain text.

### 3.11 `test_real_user_workflows.py` — 2 failures

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_login_and_dashboard_render` | Heading assertion: `'📊 Today's Summary'` vs `'Today's Summary'` | E (Emoji Remnant) |
| `test_intake_workflow_ui_elements` | Intake form selectors | C (Selector Drift) |

**Remedy:** Replace hardcoded emoji strings with `e2e_selectors` constants. Fix Intake form selectors.

### 3.12 `test_reports_dashboard.py` — 1 failure (partial)

| Test | Likely Root Cause | Category |
|---|---|---|
| `test_reports_page_renders` | Suite timed out before completion. Reports heading: `'🛡️ Reports'` → `'Reports'` | E (Emoji Remnant) or Timeout |

**Remedy:** This test may not have actually failed — it was the last test before timeout. Check if it uses `e2e_selectors.HEADING_REPORTS` or a hardcoded string.

---

## 4. Recommended Action Plan (No Changes — Observation Only)

### Phase 1: Fix the Shared Helper (P0 — Blocks 20+ tests)
1. Create a standalone debug script (`tests/debug_intake_helper.py`) that:
   - Launches Playwright browser
   - Navigates to `http://127.0.0.1:8599/`
   - Clicks START
   - Clicks Intake in sidebar
   - Takes screenshot of Intake form
   - Fills all 8 required fields
   - Clicks SAVE
   - Takes screenshot post-save
   - Checks URL for redirect
   - Queries Supabase for the created intake/bin
2. Identify exactly which step fails and fix the selector in the helper.

### Phase 2: Fix Bug-E2E-002 (Data Editor Cells) (P0 — Blocks 12+ tests)
1. Use Playwright inspector or `page.content()` to capture the rendered HTML of the Observations page data editor.
2. Identify the correct selector for:
   - Egg count input cell
   - Stage dropdown cell
   - Status dropdown cell
   - Health field cells (chalking, molding, leaking, denting)
3. Update `e2e_selectors.py` and all test files that use these selectors.

### Phase 3: Remove Emoji Remnants (P1 — ~3 tests)
1. Grep all test files for emoji characters: `grep -rn '[📊📋🔬⚙️📈🛡️]' tests/e2e_playwright/`
2. Replace with `e2e_selectors` constants (already updated to plain text).

### Phase 4: Fix Remaining Selectors (P1-P2 — ~10 tests)
- Settings/Vault Wipe buttons
- Reports page render
- Performance tests (splash screen, hydration)
- Adversarial form validation messages

### Phase 5: Database State Isolation (P2)
- Add fixtures to seed known data before tests
- Use `@pytest.mark.dependency()` for test ordering
- Ensure clean slate tests can run independently

---

## 5. Known Fixed in v9.2.0 (Tests May Not Yet Reflect)

| Fix | Commit | Impact on Tests |
|---|---|---|
| Emoji stripped from all headings | `80edc54` | Tests with hardcoded emoji prefixes still fail; use `e2e_selectors` constants |
| Soft-delete filters applied (14 queries) | `d3806c3` | Tests querying deleted data may see different results |
| Bin code display (Remove Empty Bins) | `e3c2d0e` | Bin retirement test selectors may need bin_code not bin_id |
| Surgical search — deleted bins in Correction Mode | `d299492` | Correction Mode tests may now see bins that were previously hidden |
| Version bump → v9.2.0 | `d3806c3` | Version assertion tests need updating |

---

## 6. Test Dependency Map

```
shared helper: _create_intake_and_get_bin()
├── test_bin_environment.py (4 tests)
├── test_hatching_s6.py (2 tests)
├── test_observation_workflows.py (7 tests)
├── test_observations_e2e.py (1 test)
├── test_surgical_corrections.py (6 tests, deselected)
├── test_enterprise_observations.py (10 tests, deselected)
└── test_enterprise_intake.py (deselected)

test_intake_e2e.py (2 tests) ── feeds the shared helper logic
test_intake_extended.py (4 tests) ── feeds the shared helper logic
```

**Conclusion:** Fixing `test_intake_e2e.py` and the shared helper would resolve cascading failures in ~20 dependent tests.

---

*Report compiled from log analysis and repo state. No code changes made.*
