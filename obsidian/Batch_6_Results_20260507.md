---
date: 2026-05-07 07:48
tags: [batch-6, test-results, property-matrix, escalated-to-tactic2]
status: analyzed
---

# BATCH_6 Results — 6 Rounds Failed, Escalated to Tactic 2

> [!danger] 23 tests | 6 passed | 17 failed
> All Property Matrix tests (13 across TSK-04/06/07) still fail after 6 rounds of fixes.

## Results by TSK

| TSK | Passed | Failed | Root Cause |
|-----|--------|--------|------------|
| TSK-03 | 2 | 2 | RPC creates only 1 bin (expected >=2) |
| TSK-04 | 0 | 7 | Property Matrix not rendering |
| TSK-06 | 0 | 5 | Property Matrix not rendering |
| TSK-07 | 0 | 1 | Workbench hydration failure |
| TSK-08 | 4 | 2 | SQLi WAF + XSS rejected |

## Rounds Attempted (TSDQ-001)

1. page.reload() — rejected (destroys Streamlit session cookie)
2. wait+click multi-select — failed (no rerun trigger)
3. st.stop() removal + active_bin_id — insufficient
4. env_gate_synced pre-seeding (fallback path) — insufficient
5. env_gate_synced pre-seeding (active_case_id path) — insufficient
6. START button approach (test helper) — pending validation

## Escalated to Tactic 2 Round 7

Per user directive: persistent failures need two-model strategy rethink.
