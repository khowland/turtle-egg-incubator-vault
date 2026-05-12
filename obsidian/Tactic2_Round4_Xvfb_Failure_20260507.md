---
date: 2026-05-07
tags: [tactic2, round4, xvfb, headful, failed]
status: failed
tsdq_id: TSDQ-003
reviewer: Model 2 (Claude) — APPROVED
---

# Tactic 2 Round 4: Xvfb + Headful Chromium — FAILED (Plugin Override)

> [!danger] pytest-playwright v0.7.2 FORCES --headless regardless of conftest overrides

## What We Tried

- `browser_type_launch_args` fixture with `headless: False`
- `--headed` CLI flag
- `DISPLAY=:99` with Xvfb running at 1920x1080x24
- Full process cleanup between attempts

## Result

ALL 4 attempts (v1-v4) produced Chromium processes WITH `--headless` and `--ozone-platform=headless` flags. The pytest-playwright plugin controls browser launch at a level that bypasses our conftest.py fixtures.

## Key Evidence: This May Not Be A Portal Issue

DIAG-A1 (dropdown container count: 0) and DIAG-A2 (dropdown <li> count: 0) are **consistent across ALL modes**:
- Headless Chromium (default)
- Attempted headful with Xvfb (v1-v4)
- Keyboard navigation (v4)
- Mouse click (v2)

Yet server logs PROVE:
```
[TACTIC2-DIAG] Before multiselect: workbench_bins=[553], bin_options=1
```

## New Hypothesis: Streamlit Widget Key Persistence

The `st.multiselect(key="obs_workbench")` stores widget state across Streamlit sessions. If a previous session left an empty selection, the widget **restores** that empty state and **ignores** `default=valid_defaults`.

This explains:
1. Server HAS options → but browser shows 0
2. Consistent across all interaction methods
3. DB fallback populates `workbench_bins` but widget ignores it

## Next: Tactic 2 Round 5
Fix widget key persistence — add unique session key or clear stale widget state.
