# Try Something Different Queue (TSDQ) — Governance & Methodology

**Version**: 1.0  
**Date**: 2026-05-07 00:15  
**Status**: ACTIVE  
**Author**: A0 (Deepseek) + Claude (vision)

---

## Two-Tactic Iteration Structure

### Tactic 1: Test-Fix Cycle (Standard)
```
┌──────────────────┐     ┌──────────────────┐
│ Claude (vision)  │────►│ Deepseek (coder) │
│ Tests UI         │     │ Fixes bugs       │
│ Reports failures │     │ Commits          │
│ + Remediation    │◄────│ Requests retest  │
└──────────────────┘     └──────────────────┘
         │                       │
         └─────── Repeat ────────┘
```
- **Entry**: Any test that needs execution
- **Exit**: Test passes, OR reaches 3 failures → move to TSDQ
- **Fallback**: If same failure repeats 2+ times across cycles → move to TSDQ

### Tactic 2: Strategy Rethink (For TSDQ Items)
```
┌──────────────────┐     ┌──────────────────┐
│ Model 1 (Dev)    │────►│ Model 2 (Review) │
│ Devises new      │     │ Reviews approach │
│ approach to fix  │     │ Suggests alt     │
│                  │◄────│ Refinements      │
└──────────────────┘     └──────────────────┘
         │                       │
         │   ┌──────────────────┐│
         └──►│ Model 1 (Tune)   ││
             │ Fine-tunes       │◄┘
             │ approach         │
             └────────┬─────────┘
                      │
             ┌────────▼─────────┐
             │ Model 2 (Polish) │
             │ Final refinements│
             │ Validates align  │
             └────────┬─────────┘
                      │
             ┌────────▼─────────┐
             │ Back to Tactic 1 │
             │ (test new fix)   │
             └──────────────────┘
```
- **Entry**: Item moved to TSDQ after 3+ failures or 2+ repeated same failure
- **Output**: New approach/strategy for fixing the test (code change, test refactor, or infrastructure)
- **Quality Gate**: Fix must be valid (aligns with Requirements.md, implied_system_objective.md, QA methodology). No shortcuts.
- **Exit**: New approach implemented → back to Tactic 1 for retest

## TSDQ Entry Criteria

| Criteria | Threshold |
|----------|-----------|
| Repeated same failure | 2+ occurrences |
| Total failures (same test) | 3+ |
| Systemic blocker (affects ≥3 tests) | Immediate entry |
| Timeout/Hang (not flake) | 2+ occurrences |
| Infrastructure dependency (not test bug) | 1+ occurrence |

## Tactic 2 Quality Rules

1. **No shortcuts**: Fixes must align with Requirements.md and implied_system_objective.md
2. **No mock bypassing**: DB pincer validation must remain real
3. **No test weakening**: Must not reduce assertion strength
4. **Human simulation intact**: Must test through UI, not raw SQL
5. **Objective alignment**: Must serve the turtle incubation workflow

## Queue State

