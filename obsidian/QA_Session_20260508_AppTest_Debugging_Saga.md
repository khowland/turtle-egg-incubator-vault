---
date: 2026-05-08
tags:
  - QA
  - AppTest
  - debugging
  - root-cause
  - st.session_state
  - query_params
  - bridging-bug
status: unresolved
---

# QA Session 2026-05-08 — AppTest Debugging Saga

## Summary

Attempted to migrate 13 observation workflow E2E tests from Playwright to Streamlit AppTest to bypass BaseWeb popover rendering bugs. Discovered that `st.query_params` does NOT bridge from AppTest to Streamlit script context — `st.session_state` must be used instead. Fix applied to 5 files (2 source + 3 test) but tests still timing out on `st.switch_page()`. Status: **blocked**.

## Chronology

### Phase 1: Playwright Dead-End (30+ rounds)

> [!bug] Playwright BaseWeb Popover Bug
> Streamlit's BaseWeb popover portals (used by multi-select and selectbox dropdowns) are **invisible** to Playwright locators in headless Chromium. `page.locator()` returns 0 for all `stSelectbox`, `stSelectboxVirtualDropdown`, and multi-select option elements.

**Attempted fixes**:
- v5 definitive helper (`streamlit_select_helper.py`) using `page.evaluate()` JS clicks — clicks fired but Streamlit's `on_change` handler never triggered
- `test_mode=1` query parameter — not passed through Playwright navigation
- Checkbox double-click for egg selection — Property Matrix flashed then disappeared
- `switch_page` bridging — `active_case_id` never bridged to Playwright session state

**Result**: 0/13 observation tests passed in Playwright. Decision made to switch to AppTest.

### Phase 2: AppTest Migration

> [!info] AppTest Architecture Decision
> Streamlit AppTest runs the app **in-process** — no browser, no DOM, no popover portals. Widget interactions use native API (`at.selectbox().select()`, `at.button.click()`). Session state is directly accessible.

**Created files**:
- [[test_observation_workflows.py]] — 7 test functions (512 lines)
- [[test_adversarial_observations.py]] — 5 test functions (248 lines)
- [[test_phase5_scalability_loop.py]] — 1 test function (139 lines)

> [!success] AppTest Widget Interaction Works
> Stage selectbox interaction works (`matrix_stage: 'S4'` in session state). Biological Grid checkbox selection works (`cb_*: True`). SAVE button triggers commit_batch RPC. Session state bridging works.

### Phase 3: The st.query_params Bug

> [!bug] Root Cause: st.query_params Does Not Bridge in AppTest
> `st.query_params.get("test_mode")` always returns **None** in AppTest's local script runner. Setting `at.query_params["test_mode"] = "1"` in test setup does NOT propagate to the running Streamlit script. This caused the `if not st.query_params.get("test_mode"): st.switch_page(...)` guard to fail — meaning `st.switch_page()` was called every time, crashing AppTest with `StreamlitAPIException: Could not find page`.

**Files affected**:
- `2_New_Intake.py:369` — `st.switch_page()` guard
- `3_Observations.py:525` — test_mode auto-selection handler
- `3_Observations.py:803` — `st.rerun()` guard
- All 3 test files — setting `at.query_params["test_mode"] = "1"`

### Phase 4: st.session_state Fix

> [!success] Fix Applied: Use st.session_state Instead of st.query_params
> Replaced ALL references:
> - `st.query_params.get("test_mode")` → `st.session_state.get("test_mode")` (source files)
> - `at.query_params["test_mode"] = "1"` → `at.session_state["test_mode"] = True` (test files)
> - `st.query_params.pop("test_mode")` → `st.session_state.test_mode = False`

**Status after fix**: All 5 files pass `py_compile` ✅. Fix applied to:
- `vault_views/2_New_Intake.py:368` ✅
- `vault_views/3_Observations.py:525,803` ✅
- `tests/apptest/test_observation_workflows.py` (3 refs) ✅
- `tests/apptest/test_adversarial_observations.py` (1 ref) ✅
- `tests/apptest/test_phase5_scalability_loop.py` (2 refs) ✅

### Phase 5: Tests Still Fail

> [!danger] Tests Still Timeout After st.session_state Fix
> All 13 tests still fail with `RuntimeError: AppTest script run timed out after 30(s)`. The error log shows `st.switch_page()` still being called at line 369 — implying `st.session_state.get("test_mode")` returns falsy during script execution. 

**Possible causes**:
- `st.session_state` values set before `at.run()` may not be fully bridged for ALL keys
- Timing/caching issue — session state may be reset during first `at.run()` cycle
- The `_intake_success_ui` function may run in a context where session_state test_mode flag is not visible

**Next diagnosis needed**: Add `print()` diagnostic in 2_New_Intake.py to verify what `st.session_state.get("test_mode")` returns at execution time. If session_state also fails to bridge, consider catching `StreamlitAPIException` instead of trying to prevent it.

## Test Results Timeline

| Run | Date | Fix Applied | Results |
|-----|------|-------------|---------|
| Playwright definitive | 2026-05-07 | v5 helper + test_mode | 0/13 passed (popover timeout) |
| AppTest batch v1 | 2026-05-08 | Initial AppTest files | 1/13 passed (test_mortality) |
| AppTest batch v2 | 2026-05-08 | DB timing + violation detection fix | 0/13 (SAVE button not found) |
| AppTest batch v3 | 2026-05-08 | SyntaxError fix (missing `}`) | 0/13 (SAVE button not found) |
| AppTest batch v4 | 2026-05-08 | test_mode query param | 13/13 timeout (switch_page crash) |
| AppTest batch v5 | 2026-05-08 | st.session_state fix | 13/13 timeout (switch_page still crashing) |

## Key Discoveries

1. **st.query_params does not bridge in AppTest** — must use st.session_state
2. **AppTest widget interaction WORKS** — Stage selectbox, SAVE, session state all native
3. **Playwright is fundamentally incompatible with BaseWeb popovers** — not fixable with selectors or JS evaluation
4. **AppTest can't navigate multipage apps** — st.switch_page() crashes unless guarded
5. **bin_options bloat**: 104+ accumulated bins from repeated test runs

## Related Notes

- [[Strategy_A_TestMode_20260507_2252]]
- [[Definitive_Checkbox_Fix_20260507_2048]]
- [[v5_Helper_ClickAway_Fix_20260507_1901]]
- [[TSK07_Hydration_Trigger_Fixed_20260507]]
- [[Tactic1_Batch_Retest_20260507_1400]]

## Artifacts

- `tmp/diag_mortality.log` — mortality test failure log
- `tests/apptest/` — all 3 AppTest test files
- `vault_views/2_New_Intake.py:368` — st.session_state guard
- `vault_views/3_Observations.py:525,803` — st.session_state guards

## Next Steps (for next session)

1. Add diagnostic print to confirm `st.session_state.get("test_mode")` value
2. If session_state also doesn't bridge → catch StreamlitAPIException instead of preventing it
3. Fix remaining TSK-03 (2 RPC bugs) and TSK-08 (selector drift) 
4. Run full QA matrix: 39 green + 13 AppTest + 6 Playwright = 58 tests total
