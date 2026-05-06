# NEEDS_WORK: TSK-03 — test_intake_extended.py

**Status:** HARD_LOCK (Strike 3)
**Date:** 2026-05-05 01:44 UTC-5
**Role:** Runner

---

## Executive Summary

TSK-03 (`test_intake_extended.py`) was executed as Runner after Validator static analysis passed (dvn-cell fix applied per Bug-E2E-002 resolution). **3 out of 4 tests failed**, all during the data_editor (egg count) interaction phase after filling all required intake fields. The only passing test (`test_intake_cancel_button`) does not use the data_editor.

---

## Failure Root Cause

**Bug-E2E-002 (stale data_editor locator) was partially resolved but the dvn-cell fix does not survive a FULL intake form fill.**

### What works (TSK-05, 7/7 pass):
- `_fill_required_fields_minimal` helper: fills Species, Condition, Days in Care, Egg Collection Method, Circumstances, and Weight.
- After this, `div[data-testid='stDataFrame'] div.dvn-cell` is reliably locatable.
- All 7 adversarial intake tests pass with the dvn-cell + double-click/keyboard pattern.

### What fails (TSK-03, 3/4 fail):
- `_fill_intake_step1_fields` helper adds a **1500ms Streamlit rerender wait after the Species selectbox** (line 42: `page.wait_for_timeout(1500)`) plus additional selectbox interactions (Condition, Egg Collection Method).
- After this comprehensive field population, the Streamlit data_editor component has been re-rendered by the framework, and the initial `div[data-testid='stDataFrame']` may not yet contain visible `div.dvn-cell` cells, OR the cell locator is detached/stale after the rerender.
- Result: `TimeoutError: Locator.dblclick: Timeout 30000ms exceeded. waiting for locator("div[data-testid='stDataFrame']").locator("div.dvn-cell").filter(has_text="1").first`

---

## Test Details

| Test | Status | Notes |
|:---|:---|:---|
| `test_intake_full_fields_and_bin_nomenclature` (TC-INT-01) | FAILED | dvn-cell timeout after `_fill_intake_step1_fields` |
| `test_intake_multiple_eggs` (TC-INT-02) | FAILED | Same dvn-cell timeout |
| `test_intake_cancel_button` (TC-INT-03) | PASSED | No data_editor interaction |
| `test_supplemental_intake_full_save` (TC-SUP-01) | FAILED | Creates primary intake first → dvn-cell timeout |

### Terminal Output (first failing test)

```
tests/e2e_playwright/test_intake_extended.py::test_intake_full_fields_and_bin_nomenclature[chromium] FAILED
tests/e2e_playwright/test_intake_extended.py::test_intake_multiple_eggs[chromium] FAILED
tests/e2e_playwright/test_intake_extended.py::test_intake_cancel_button[chromium] PASSED
tests/e2e_playwright/test_intake_extended.py::test_supplemental_intake_full_save[chromium] FAILED
```

---

## Suggested Remediation Path

1. **Option A: Add `page.wait_for_timeout(2000)` after the final wait in `_fill_intake_step1_fields`** to give Streamlit time to fully re-render the data frame after all field fills.
2. **Option B: Add `data_frame.first.wait_for(timeout=10000)` with `page.wait_for_timeout()` fallback** similar to the try/except pattern that works for TSK-05's `test_zero_eggs_rejected`.
3. **Option C: Investigate if the 1500ms wait after Species causes a DOM refresh** that invalidates the dvn-cell locator; try removing it or adding a second rerender wait after the complete field set.
4. **Option D: Use Playwright's `wait_for()` for the data frame to be visible AND contain cells** before attempting interaction.

---

## Affected Files
- `tests/e2e_playwright/test_intake_extended.py` — lines 98-99 call `_fill_intake_step1_fields`, lines 158-163 use dvn-cell
- `tests/e2e_playwright/test_observation_workflows.py` (TSK-04) — uses similar `_setup_intake_and_unlock_grid` helper (line 22-117) with full selectbox workflow. **TSK-04 is at Strike 2 READY_TO_RUN and MUST NOT be executed until this issue is resolved.**

---

## Ledger Update Required

- TSK-03: `[HARD_LOCK]`, moved to Strike Out table
- TSK-04: Return to `[TODO]` with note about shared dvn-cell-after-full-fill issue
