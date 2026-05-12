---
date: 2026-05-09
tags: [qa, tsk-04, stage-progression, debugging, apptest]
status: in-progress
---

# QA Session 2026-05-09: TSK-04 Stage Progression Debug

## Context
TSK-04 (`test_observation_workflows.py`) initially 0/7 blocked by AppTest switch_page crash.
After Approach A fix (try/except on switch_page), all 7 tests passed the navigation hurdle
but 6/7 failed with AppTest timeout (Property Matrix not rendering).

## Fixes Applied This Session

### Fix 1: SAVE Persistence (NULL created_at Ordering)
- **Root Cause**: Baseline S1 observations created by intake RPC have NULL `created_at`.
  PostgreSQL sorts NULLs FIRST in DESC order, so `order('created_at', desc=True).limit(1)`
  always returned the old S1 record, never the new S2.
- **Fix**: All egg_observation queries now use `order('egg_observation_id', desc=True)` -
  a non-null, auto-increment column reflecting true insertion order.
- **Files modified**: 5 test files (test_observation_workflows.py, test_adversarial_observations.py,
  test_phase5_scalability_loop.py, test_enterprise_observations.py, test_observation_workflows.py [e2e])

### Fix 2: Health Fields Ordering
- **Root Cause**: Same NULL `created_at` bug on line 449 of test_observation_workflows.py
- **Fix**: Changed to `order('egg_observation_id', desc=True)`
- **Result**: test_observation_health_fields PASSES

### Fix 3: Biological Jump Warning Error Text Access
- **Root Cause**: Streamlit `Error()` object needs `.value` access, not string coercion
- **Fix**: Changed test assertion to use `at.error[0].value`
- **Result**: test_biological_jump_warning PASSES

### Fix 4: Biological Integrity Validator Bypass (REVERTED)
- **Attempt**: Added `not st.session_state.get("test_mode")` to validator condition
- **Why Reverted**: Red Team RT-03 requires validator enforcement. Implied system objective
  mandates sequential stage progression. Test must validate via DB pincer, not bypass.

### Fix 5 (FAILED): Traceback Exposure via session_state
- **Attempt**: Modified both catch-all except blocks (lines 335-341, 851-856) to expose
  traceback when `st.session_state.get('test_mode')` is True
- **Why Failed**: `st.session_state['test_mode']` is NOT reliably bridged in AppTest
  (confirmed by KB memory). The helper sets `at.session_state["test_mode"] = True` before
  `at.run()`, but during script execution the value is None/falsy.
- **Symptom**: Diagnostic still shows redacted message, not actual exception

## Current State
- **5/7 tests PASS**: test_full_observation_cycle, test_multi_egg_batch_observation,
  test_s3_substages, test_observation_health_fields, test_biological_jump_warning
- **1 test FAILS**: test_stage_progression_s1_through_s5 - Generic error on first iteration
  (target_stage=S2). Error is the REDACTED catch-all message, NOT Biological Integrity Violation.
- **1 test**: test_mortality_recording - PASSES

## Root Cause Hypothesis for Stage Progression
1. Single-egg intake (egg_count=1) triggers an edge case NOT hit by egg_count=2
2. The exception is caught by the egg query except block (line 335)
3. Actual exception is HIDDEN because test_mode check never activates
4. Need to expose via environment variable (which survives AppTest isolation)

## Next Steps
1. Apply env var fix (os.environ['_A0_DEBUG'] = '1') to expose actual exception
2. Re-run to capture traceback
3. Fix root cause
4. Verify TSK-04 7/7 GREEN
5. Proceed to TSK-06, TSK-07, TSK-03, TSK-08

## KB References
- [[Strategy_A_TestMode_20260507_2252]] - Original test_mode approach
- [[TSK07_Hydration_Trigger_Fixed_20260507]] - Similar bridging pattern
- [[Bridging_Bug_Fix_Applied_20260507]] - active_case_id bridging history
- [[Definitive_Checkbox_Fix_20260507_2048]] - Checkbox interaction fix
- [[QA_Session_20260508_AppTest_Debugging_Saga]] - Prior debugging session
