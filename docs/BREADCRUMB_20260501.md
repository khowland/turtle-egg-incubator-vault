# Breadcrumb — 2026-05-01 01:26 CST

## Current State

### What's completed
- Change request CR-20260430-181500 (New Intake bug fixes + workflow) created, formatted, merged into master CR.
- Change request CR-20260430-194500 (Data Architecture Integrity & System Refactoring) created and reviewed.
- Implementation plan drafted, then reviewed by developer-profile engineering peer.
- V2 plan saved: `/a0/usr/workdir/change_requests/CR-20260430-194500_IMPLEMENTATION_PLAN_v2.md`
- Previous CR status updated: `change_requests/change_request_20260430181500.txt` marked CLOSED.

### Key Files
| File | Purpose |
|------|---------|
| `change_requests/CR-20260430-194500_IMPLEMENTATION_PLAN_v2.md` | Master implementation plan (peer-reviewed) |
| `change_requests/CR-20260430-194500_IMPLEMENTATION_PLAN.md` | Original plan (pre-review) |
| `change_requests/change_request_20260430194500.txt` | Source CR |
| `docs/implied_system_objective.md` | Guiding principles for all changes |
| `docs/design/Requirements.md` | System requirements |
| `docs/turtle_expert_interview.md` | Expert clinical guidance |
| `claude.promptinclude.md` | Engineering methodology (commits, breadcrumbing, testing) |

### Next Steps (from v2 plan)
1. Phase 0: Pre-flight schema audit, backup, archive outdated migrations.
2. Phase 1: Schema corrections + RPC updates (temperature columns, observer_id).
3. Phase 2: Error handling fixes (safe_db_execute).
4. Phase 3: UI changes — 2_New_Intake.py (labels, bin config grid, supplemental mode).
5. Phase 4: UI changes — 3_Observations.py (rename ambient_temp, remove sidebar tools).
6. Phase 5: UI changes — 5_Settings.py (verify backup/restore, seed lookup tables).
7. Phase 7 (original Phase 6): PK/FK standardization — RECOMMENDED DEFERRAL to dedicated CR.
8. Phase 8: Testing updates.
9. Phase 10: Final verification.

### Execution Strategy
- Agent0 (coordinator) reviews, verifies, and tests work done by developer-profile sub-agents.
- Each task is dispatched to a fresh subordinate with `reset=true` to keep token weight low.
- After each task: test, commit, and advance.
- All changes must align with `docs/implied_system_objective.md` and `docs/design/Requirements.md`.

### Git tag checkpoint
- Tag `pre-cr-20260430-refactor` should be created before starting Phase 1.
