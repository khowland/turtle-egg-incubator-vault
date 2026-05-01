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

## Update — 2026-05-01 ~05:45 CST (CR-20260430-194500 Phases 0-7 Complete)

### Completed Phases
- Phase 0: Preparation — backup, version bump (v8.1.27→v9.0.0), preflight audit, archive old migrations, rollback procedures
- Phase 1: Schema & RPC — renamed ambient_temp→incubator_temp_f, updated all RPCs, added observer_id to system_log
- Phase 2: Error Handling — conditional observer_id in log_entry, dual error propagation fix (return False)
- Phase 3: UI — 2_New_Intake.py (labels, bin grid redesign, supplemental mode, removed mass/temp from intake)
- Phase 4: UI — 3_Observations.py (incubator_temp_f rename, removed supplemental tools sidebar)
- Phase 5: UI — 5_Settings.py verified, lookup tables seeded (12 species, 21 stages, 41 properties)
- Phase 6: PK/FK — transitional bin_code and egg_stage_code columns added
- Phase 7: Testing — existing tests updated, 7 new test files created, e2e Playwright tests updated

### New Migration Files
- v8_3_0_UPDATE_ALL_RPCS_FOR_TEMP_RENAME.sql
- v8_3_2_CONSOLIDATE_BIN_OBS_TEMP.sql
- v8_3_3_ADD_OBSERVER_ID_TO_SYSTEM_LOG.sql
- v8_3_5_SEED_LOOKUP_TABLES.sql
- v8_4_1_ADD_BIN_CODE.sql
- v8_4_2_ADD_EGG_STAGE_CODE.sql

### Next Steps
- Phase 8: Documentation (in progress)
- Phase 9: Deployment Verification & CR Sign-off
