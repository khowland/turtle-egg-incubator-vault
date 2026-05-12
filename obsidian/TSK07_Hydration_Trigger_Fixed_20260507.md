---
title: "TSK-07 Hydration Trigger Fixed - 2026-05-07"
date: 2026-05-07
tags: [qa, bugfix, tsk-07, hydration, portal, conftest]
status: fix-applied
---

# TSK-07: Hydration Trigger Fixed

> [!success] **Root cause found and fixed**

## Discovery
Diagnostic trace proved the Observations page IS hydrated after intake setup:
- Server logs: `workbench_bins=[568], bin_options=2`
- Browser: multi-select=True, checkboxes=2, selectbox=1
- Popover: LI count from evaluate works

## Root Cause
The `_trigger_workbench_hydration()` function in `conftest.py` used Playwright locators
to detect multi-select options — but locators always return 0 for portal-rendered
popover elements in headless Chromium. The page was correctly hydrated all along;
the trigger function just couldn't detect it.

## Fix
Rewrote `_trigger_workbench_hydration()` to use `page.evaluate()` for direct DOM
inspection of the BaseWeb popover, bypassing Playwright's locator limitation.

## Related
- [[Tactic1_Batch_Retest_20260507_1400]]
- [[Test_Team_Architecture]]
