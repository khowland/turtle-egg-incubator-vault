# Bug-E2E-002: Data Editor Cell Selector Stale in v9.0.0

**Status:** ❌ OPEN  
**Date:** 2026-05-03  
**Affected Tests:** test_enterprise_observations.py, test_observation_workflows.py, test_surgical_corrections.py  
**Priority:** 🔴 HIGH

## Description

After the v9.0.0 UI changes (data editor component for egg count input), the old selector for the egg count cell no longer matches. The Streamlit data editor does not expose consistent `role="gridcell"` selectors; instead it uses a custom container with text input. E2E tests using `page.get_by_role("gridcell")` or similar fail to locate the cell.

## Symptoms
- Tests fail with "Element not found" when trying to fill egg count
- Affects all observation workflows, surgical corrections, and S6 hatching
- Passes in earlier versions (v8.x) where a simple text input was used

## Investigation
- The data editor uses `[data-testid="stDataFrame"]` or `div[data-baseweb="data-table"]`
- Cell selectors in Playwright need to target `input` elements within data editor rows
- Exact selector depends on the current Streamlit version

## Plan
1. Inspect the rendered HTML of the data editor in v9.2.0
2. Identify the correct selector for the egg count input
3. Update all affected test files
4. Re-run E2E suite to verify resolution

## Related
- [[SoftDelete_Audit|Soft-Delete Audit]] - also a mandate that could affect data shown in editor
