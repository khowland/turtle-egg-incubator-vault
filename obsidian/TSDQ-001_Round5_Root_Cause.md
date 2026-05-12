---
date: 2026-05-07 02:00
tags: [tsdq-001, root-cause-found, session-id-mismatch, weight-gate]
status: fix-applied
---

# TSDQ-001 Round 5: Root Cause Found

> [!success] True Root Cause
> The weight gate's DB check compares `bin_observation.session_id` with `st.session_state.session_id`. The RPC creates the initial observation during intake SAVE with a **server-side session_id** that doesn't match the **Playwright browser's session_id**. This mismatch causes `env_gate_synced` to remain `False`, which triggers `st.stop()` and blocks the egg grid + Property Matrix.

## Two Scenarios, Two Fixes

### 1. Fallback Path (no intake linked) — Fixed in Round 4
Pre-seeded `env_gate_synced=True` for all bin_options.

### 2. New Intake Path (active_case_id set) — Fixed in Round 5
After populating workbench_bins from active_case_id, pre-seed `env_gate_synced=True` for all intake-sourced bins. The intake SAVE RPC already recorded the initial weight — no re-weighing needed.

## Files Changed
- `vault_views/3_Observations.py` lines 54-61: Pre-seed env_gate_synced after active_case_id bin population
