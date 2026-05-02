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

### Phase 8 & 9 Completion (2026-05-01 ~06:00 CST)
- Phase 8: Documentation — requirements.md updated (§3.1, §3.2, §4.5, §4.6), schema export updated for new columns, operator manual updated with new UI labels, rollback procedures validated against actual migrations
- Phase 9: Deployment Verification — all migrations applied and verified, test suite run: 20 passed, 2 failed (pre-existing AppTest timeouts), 1 skipped (no live Supabase); all 7 CR-specific tests pass, e2e Playwright tests updated
- CR-20260430-194500 status set to RESOLVED
- All work committed and pushed to origin/main

## Update — 2026-05-01 17:27 CST (CR-20260429-210932 Resolved)

### Completed
- CR-20260429-210932: Auto-Increment Bin Code in "Add Bin to Intake" + Match Initial Intake Form Format
  - Enhanced existing bin loading: bin_num parsed from actual bin_id suffix for accurate numbering (lines 110-130)
  - Auto-increment computation: computes next bin number from existing bin_id suffixes, builds next_bin_code (lines 196-230)
  - Structured "Add Bin to Intake" expander in supplemental mode: read-only auto-generated bin code preview, Bulk Egg Count input, Egg Intake Date input, "Add This Bin" button (lines 234-276)
  - Conditional num_rows: fixed for supplemental mode, dynamic for new intake (line 278-282)
  - Guarded bin_id_preview: existing bins keep actual bin_id, new bins use formula with assigned bin_num
  - Syntax check passed, 2 supplemental intake tests passed
  - Commit: 9f68c83 "CR-20260429-210932: Auto-increment bin code and structured add-bin form"
- File: vault_views/2_New_Intake.py (82 insertions, 5 deletions)
- Status: RESOLVED

### Remaining Work (per project state as of 2026-05-01)
- CR-20260426-173831 (PENDING AUTH, LOW) — Mobile UX CSS fix, 1 file
- CR-20260426-145540 deferred: DB-1/DB-2 restore snapshot overhaul, St-2 species codes (HOLD), St-4 flag field (HOLD)

## Update — 2026-05-01 19:34 CST (CR-20260501-1800 Resolved — Numeric PK/FK Migration)

### Completed
- CR-20260501-1800: Full Numeric PK/FK Migration — Convert bin.bin_id and development_stage.stage_id to Numeric Surrogate Keys
  - **Phase A**: TRUNCATE all 8 transaction tables (hatchling_ledger, egg_observation, bin_observation, egg, bin, intake, session_log, system_log) — lookup tables preserved
  - **Phases B-F**: Convert bin.bin_id from text → BIGINT GENERATED ALWAYS AS IDENTITY; update FK columns in egg, bin_observation, egg_observation; re-add FK constraints
  - **Phase G**: Convert development_stage.stage_id from text → BIGINT GENERATED ALWAYS AS IDENTITY; update FK in biological_property
  - **Phase H**: Re-seed lookup tables (15 development stages, 41 biological properties) with correct numeric FK references
  - **Schema verified**: bin.bin_id = BIGINT IDENTITY, bin.bin_code = text; stage_id = BIGINT IDENTITY, egg_stage_code = text
  - **SQL migration**: supabase_db/migrations/v9_1_0_NUMERIC_PK_MIGRATION.sql (216 lines, applied via Supabase Management API, HTTP 201)
  - **Python views updated**: 2_New_Intake.py, 3_Observations.py, 6_Reports.py — all use bin_code for display, numeric bin_id for internal ops
  - **Tests updated**: 7 mock test files patched with numeric bin_id + bin_code fields; test_bin_id_logic.py updated; test_clinical_record_lifecycles.py updated
  - **Documentation**: Requirements.md §1.6 added (Numeric Surrogate Keys DB §36 standard)
  - **Change request**: change_requests/change_request_20260501_1800_pk_migration.txt created and marked RESOLVED
- Status: RESOLVED

### Remaining Work (per project state as of 2026-05-01)
- CR-20260426-173831 (PENDING AUTH, LOW) — Mobile UX CSS fix, 1 file
- CR-20260426-145540 deferred: DB-1/DB-2 restore snapshot overhaul, St-2 species codes (HOLD), St-4 flag field (HOLD)
