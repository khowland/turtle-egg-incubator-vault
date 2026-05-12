# TSDQ Items — Try Something Different Queue

| ID | Component | Rounds | Status | Approach |
|----|-----------|--------|--------|----------|
| TSDQ-001 | Multi-select workbench (bridging) | 6 | 🔄 Round 7 pending | START button approach tested |
| TSDQ-002 | RPC vault_finalize_supplemental | 3 | ⏸️ Waiting | Backend fix needed |
| TSDQ-003 | Selectbox dropdown (render order) | 1 | 🔄 Round 2 pending | Keyboard failed → fix Observations.py render order |

## Tactic 2 Round Log

### TSDQ-003 Round 1: Keyboard Navigation v4
- **Model 1 (Deepseek)**: Proposed keyboard navigation (Tab/Space/type/Enter)
- **Model 2 (Claude)**: APPROVED_WITH_CHANGES — 7 refinements
- **Result**: FAILED — popover opened but dropdown has 0 options (render-order bug)
- **Root cause discovered**: workbench_bins is empty at multi-select widget render time

### TSDQ-003 Round 2: Fix Observations.py Render Order (PENDING)
- **Model 1 (Deepseek)**: Move workbench_bins population ABOVE multi-select widget render
- **Model 2 (Claude)**: [PENDING REVIEW]
