# TSK-04 Intake Navigation Fix
**Date:** 2026-05-12
**Author:** Agent Zero (QA Architect / CIE)
**Status:** Implemented

## Problem
The test helper `_setup_intake_and_unlock_grid` used sidebar link click (`a:has-text('Intake')`) to navigate to the Intake page. In headless Playwright, this locator timed out because the sidebar navigation may not reliably render after login.

## Fix
Replace sidebar link click with direct URL navigation to `/2_New_Intake` using `page.goto()`. This mirrors the pattern already used for Observations navigation with query parameters.

## Code Change
In `tests/e2e_playwright/test_observation_workflows.py`, lines 23-25:
- Old: `page.locator(NAV_INTAKE).first.click()` + wait for heading "Step 1"
- New: `page.goto(f"{base_url}/2_New_Intake")` + wait for species selectbox

This eliminates dependency on sidebar rendering and aligns with the bridging fix approach.
