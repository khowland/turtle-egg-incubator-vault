---
date: 2026-05-07
tags: [tsdq, tactic2, selectbox, playwright, streamlit, headless, blocking]
status: escalated
tsdq_id: TSDQ-003
component: Streamlit BaseWeb selectbox dropdown
blocked_tests: TSK-04, TSK-06, TSK-07 (13+ tests total)
---

# TSDQ-003: Streamlit Selectbox Dropdown Won't Open in Headless Playwright

> [!danger] BLOCKER — Systemic Playwright-Streamlit incompatibility

## Problem

After **15+ rounds** of Tactic 1 (test → fix → retest) and **v2 shared helper** (red-team approved with all 5 security/safety fixes), the Streamlit BaseWeb selectbox dropdown still won't open reliably in headless Chromium via `page.mouse.click()`.

### Symptoms
- `[SELECT-HELPER] Post-selection value for 'Stage': ✅ Stage` — verification reads the label text, NOT the selected option
- Dropdown (`stSelectboxVirtualDropdown`) never appears in DOM
- Real mouse clicks at bounding box coordinates don't trigger React's onChange

## Root Cause Analysis

Streamlit uses BaseWeb components with **portal-based React dropdowns**. In headless Chromium:
1. `page.mouse.click()` dispatches a DOM MouseEvent
2. React's synthetic event system may or may not process it
3. The portal dropdown is conditionally rendered by React state, not DOM mutation
4. Headless mode's event pipeline differs from headful — potential timing/rendering mismatch

## Tactic 2 Required

Per QA_TSDQ_GOVERNANCE.md: This failure survived Tactic 1 → escalate to Tactic 2 queue.

## Proposed New Approach

**KEYBOARD NAVIGATION**: Use browser-native Tab/Enter/Arrow keys to interact with selectboxes.

Rationale:
- Keyboard events are processed differently than mouse events in Chromium
- Tab navigation uses browser focus system (reliable in headless)
- Space/Enter opens dropdowns via native key handlers
- Arrow keys navigate options via listbox ARIA patterns
- More faithful to real user interaction than `page.evaluate()` shortcuts
- Aligns with QA methodology: no shortcuts, valid fixes only

## Next Steps
1. A0 devises keyboard navigation approach
2. Claude (Model 2) red-team reviews it
3. 2 back-and-forths to refine
4. Implement
5. Back to Tactic 1 testing

## Blocked Tests

| TSK | File | Tests | Symptom |
|-----|------|-------|---------|
| TSK-04 | test_observation_workflows.py | 7 | Stage selectbox hang |
| TSK-06 | test_adversarial_observations.py | 5 | Stage selectbox timeout |
| TSK-07 | test_phase5_scalability_loop.py | 1 | Stage selectbox timeout |
| **Total** | | **13** | |

---

## Tactic 1 History (all failed)

| Round | Approach | Result |
|-------|----------|--------|
| 1-5 | page.locator().click() | Dropdown never appeared |
| 6-8 | page.mouse.click() at coordinates | Same |
| 9-10 | page.evaluate() dispatchEvent | Opened but options not clickable |
| 11-12 | v1 shared helper | Same |
| 13-15 | v2 red-team approved helper | Verification reads label, not value |
