---
date: 2026-05-07T20:48:09.198566
tags: [qa, breakthrough, definitive-fix, checkbox, start-button, tsk-04]
status: applied
---

# DEFINITIVE FIX: Checkbox Double-Click Replaces START Button

## Root Cause (Confirmed)
- RPC `vault_finalize_intake` creates S1 baseline `egg_observation` records for ALL eggs at intake SAVE
- `observed_ids` set contains every egg → `pending_eggs` (eggs NOT in observed_ids) is EMPTY
- START button (line 525, 3_Observations.py) selects only pending eggs → selects ZERO
- `selected_eggs` stays empty → Property Matrix (line 583: `if selected_real_ids:`) never renders
- Stage selectbox (line 596-601) only exists INSIDE Property Matrix → never in DOM
- ALL 12 observation tests fail with `RuntimeError: Failed to select stage S2`

## Fix Applied
Replaced all 7 `page.get_by_role("button", name="START").click()` calls in TSK-04 with:
```python
checkboxes = page.get_by_role("checkbox").all()
if checkboxes:
    checkboxes[0].click()  # deselect (is_done=True → False)
    page.wait_for_timeout(500)
    checkboxes[0].click()  # reselect (False → True) triggers st.rerun()
    page.wait_for_timeout(2000)
```

## Why This Works
- Checkboxes start CHECKED (is_done=True) because eggs already have S1 baseline observations
- Deselect click unchecks → Reselect click re-checks → triggers `st.rerun()`
- After rerun, `selected_eggs` is populated → Property Matrix renders → Stage selectbox appears

## Files Modified
- `tests/e2e_playwright/test_observation_workflows.py`: 7 START clicks → checkbox double-click

## Files Already Fixed
- `tests/e2e_playwright/test_phase5_scalability_loop.py`: Already uses checkbox double-click
- `tests/e2e_playwright/test_adversarial_observations.py`: No START clicks (different pattern)

## AST Verification
- TSK-04 AST: CLEAN (506 lines, 0 remaining START clicks)
