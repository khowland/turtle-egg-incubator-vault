---
date: 2026-05-07 05:10
tags: [qa, tactic2, tsdq, workbench-hydration]
status: escalated
---

# TSDQ-002 Escalation: Workbench MultiSelect Hydration

> [!danger] 13 tests blocked across TSK-04/06/07
> After 10+ Tactic 1 rounds, the workbench multi-select returns 0 dropdown options for newly created intakes.

## Evidence
- Flex fix diagnostic: `[DIAG] Total dropdown options: 0`
- Search pattern: bin_code='WT142-OBS-SETUP-1778148064-1' → fallback bin_id='543' → no match
- TACTIC2 shows workbench_bins=[542] but for DIFFERENT active_case_id (I2026050709572)
- Test creates NEW intake each run, but workbench shows stale bins from previous intake

## Hypothesis
active_case_id not bridged to new intake after creation. The Observations page shows bins from a different (old) intake.

## Tactic 2 Plan
Model 1 (Deepseek) investigates: how does active_case_id get set after intake creation? Is it via URL parameter? Session state? Can the test explicitly set it?
Model 2 (Claude) reviews findings and validates approach.
