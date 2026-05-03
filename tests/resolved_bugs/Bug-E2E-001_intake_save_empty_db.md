# Bug-E2E-001: Intake SAVE Produces Empty Query Results in E2E Test Helpers

**Status:** OPEN  
**Date Found:** 2026-05-03  
**Severity:** CRITICAL — Blocks all bin_environment and enterprise_observations tests  
**Files Affected:**
- `tests/e2e_playwright/test_bin_environment.py::_create_intake_and_get_bin`
- `tests/e2e_playwright/test_enterprise_observations.py::_setup_intake_and_unlock_grid`
- `tests/e2e_playwright/test_enterprise_intake.py`

---

## Symptoms
- `IndexError: list index out of range` at helper line where `intake.data[0]` is accessed
- The intake query `db.table("intake").select("intake_id").eq("intake_name", sig).execute()` returns empty data
- Clicking SAVE button via Playwright does not create the intake row in the database

## Root Cause Hypothesis
1. **Strict mode violation**: `get_by_label("Finder")` and `get_by_label("WINC Case #")` resolve to 2 elements (help button + textbox), causing fill to fail silently
2. **Post-SAVE navigation**: `st.switch_page` redirects before DB write completes, or the Observations heading with emoji is not detected
3. **Intake validation**: The form may have required fields not being filled (e.g., species selection, bin code template)

## Debugging Steps
1. Use live browser to manually perform Intake SAVE and observe actual behavior
2. Verify form fields are being filled correctly
3. Check for validation errors or required fields not met
4. Confirm the correct SAVE button is being clicked (not a different SAVE on the page)

## Proposed Fix
- Replace `get_by_label()` with `get_by_role("textbox", name="...")` to avoid strict mode violations
- Wait for success toast before navigating away
- Verify intake_name exists before querying bins

---

## Resolution
*(To be filled after fix is validated)*
