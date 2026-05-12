---
date: 2026-05-07T10:50:50
tags: [qa, tactic2, root-cause, navigation]
status: fix-implemented
---

# Root Cause: Browser renders Dashboard instead of Observations

> [!important] Model 2 (Claude) identified definitive root cause
> The browser renders Dashboard (📊 icon), NOT Observations (🔬 icon).
> Observations Python code executes server-side (TACTIC2 diagnostics confirm), but browser never navigates there.

## Evidence
- TACTIC2 diagnostic: `workbench_bins=[544], bin_options=1` (server-side)
- DOM diagnostic: `[DIAG-A5] Page text: 📊 No results` (Dashboard, not Observations)
- Observations uses 🔬 icon, Dashboard uses 📊

## Fix Applied
1. Test helper `_setup_intake_and_unlock_grid` now uses `page.goto('http://127.0.0.1:8599/3_Observations')` instead of clicking sidebar link
2. Added navigation diagnostic to verify correct page loads
3. Replaced `triple_click()` with `click()` for weight gate input

## Impact
This was the systemic blocker for TSK-04 (7 tests), TSK-06 (5 tests), TSK-07 (1 test). Fix should unlock 13 previously blocked tests.
