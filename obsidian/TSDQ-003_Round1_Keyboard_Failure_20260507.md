---
date: 2026-05-07
tags: [tsdq, tactic2-round1, keyboard, failed, root-cause]
status: failed
tsdq_id: TSDQ-003
parent: TSDQ-003_Escalation_20260507
---

# TSDQ-003 Round 1: Keyboard Navigation v4 — FAILED

> [!danger] Popover opened but dropdown has ZERO options

## Test Result

```
[KBD-HELPER] Attempt 1: Selectbox 'Stage' input not found
[KBD-HELPER] Attempt 2: Popover portal opened ✓
[KBD-HELPER] Attempt 2: Input value = ''
[KBD-HELPER] Attempt 2: Value mismatch, trying End key fallback
[KBD-HELPER] Attempt 2 End-fallback: Input value = ''
[KBD-HELPER] Attempt 3: Popover portal did not appear after Space
[KBD-HELPER] ❌ Failed to select 'S2' from 'Stage' after 3 attempts
```

## Root Cause Analysis

Keyboard navigation WORKED technically (popover opened on attempt 2). The failure is NOT about keyboard events — it's about the dropdown having **zero options**.

Page diagnostics confirm:
```
[DIAG-A1] Dropdown container count: 0
[DIAG-A2] Dropdown <li> count: 0
```

The Observations page renders the multi-select widget BEFORE `workbench_bins` is populated by the bridging fix. Streamlit renders widgets synchronously during page script execution. The fix flow is:

1. Page loads → multi-select renders with `workbench_bins=[]` → 0 options
2. Bridging fix populates `workbench_bins` → too late, widget already rendered
3. No amount of mouse/keyboard magic can select from an empty dropdown

## Next: Tactic 2 Round 2

Fix the RENDER ORDER — ensure workbench_bins is populated BEFORE the multi-select widget renders.
