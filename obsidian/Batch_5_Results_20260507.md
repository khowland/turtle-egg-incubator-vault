---
date: 2026-05-07 01:45
tags: [batch-5, comprehensive-test, hydration-gate-fix]
status: analyzed
---

# Batch 5 Results — Comprehensive Retest After env_gate_synced Fix

> [!danger] 23 tests, 7 passed (30%), 16 failed
> The HYDRATION GATE pre-seeding fix (env_gate_synced=True for all bin_options) did NOT resolve the Property Matrix rendering issue.

## Results Summary

| TSK | Passed | Failed | Key Issue |
|-----|--------|--------|-----------|
| TSK-03 (intake_extended) | 3 | 1 | Supplemental RPC bug (bin count 1 vs >=2) |
| TSK-04 (observation_workflows) | 0 | 7 | Property Matrix not rendering after egg selection |
| TSK-06 (adversarial_observations) | 0 | 5 | Same Property Matrix cascade |
| TSK-07 (scalability_loop) | 0 | 1 | Workbench hydration failed (same root cause) |
| TSK-08 (adversarial_input) | 4 | 2 | SQLi WAF 403 + XSS storage mismatch |

## Critical Failure: Property Matrix Still Not Rendering

Diagnostic output confirms:
```
[DIAG] Clicking first egg checkbox label (visible label triggers hidden input)...
[DIAG] After double-click - Property Matrix visible: False
```

Despite env_gate_synced=True pre-seeding, the Property Matrix (which contains Stage selectbox, checkboxes, SAVE button) never renders after egg selection. This is now 4 rounds of failed fixes:
1. Round 1: page.reload() rejected (destroys session)
2. Round 2: wait+click failed (multi-select click doesn't trigger rerun)
3. Round 3: st.stop() + active_bin_id insufficient
4. Round 4: env_gate_synced pre-seeding insufficient

## Escalated to Tactic 2 Round 5

Two-model strategy rethink needed.
