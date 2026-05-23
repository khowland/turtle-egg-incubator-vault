# BREADCRUMB — observer_name Schema Alignment & Code Audit
**Date:** 2026-05-22  
**Branch:** feature/react-resurrection  
**Summary:** Renamed `display_name` → `observer_name` across all active source files to match DB schema. Conducted enterprise code audit with 12 findings; resolved all CRITICAL and HIGH items. Verified via A2-DB Auditor subagent. Clean chat handoff ready.

---

## Phase 1: `display_name` → `observer_name` Rename ✅ COMMITTED

**Commit:** `862e6ad` (and predecessor)  
**Files changed (9):**
- `frontend/src/pages/Login.tsx` — select, order, map
- `frontend/src/pages/Settings.tsx` — interface, select, order, form fields, deleteConfirm
- `frontend/src/lib/identity.ts` — comment updated
- `utils/session.py` — select, observer_options dict
- `vault_views/5_Settings.py` — select, column_config, row mapping
- `tests/test_session_resilience.py` — mock data
- `tests/test_session_termination.py` — mock data (2 occurrences)
- `tests/test_vault_logic.py` — mock data
- `tests/test_ui_smoke_checks.py` — mock data
- `tests/test_workflow_settings_renders.py` — mock data
- `tests/clinical_edge_cases/test_surgical_logic.py` — mock data

**DO NOT TOUCH (archived, ignore):**
- `backups/cr194500/observer.json` — historical backup
- `turtledb_schema_generated_*.txt` — auto-generated schema dumps
- `schema_dump_*.sql` — backup dumps
- `db_schema_export.txt.old` — old export
- `mid_season_golden_snapshot.json` — snapshot artifact
- `.venv/` and `node_modules/` — dependencies

---

## Phase 2: Enterprise Code Audit — Resolved Items ✅ COMMITTED

**Commit:** `862e6ad`  
**Files changed (3):**
- `frontend/src/lib/identity.ts`
- `frontend/src/pages/Intake.tsx`
- `frontend/src/components/Sidebar.tsx`

### CRITICAL — FIXED
1. **`ensureSessionPersisted` inserted `session_id` (GENERATED ALWAYS AS IDENTITY)** — Now lets DB auto-generate; returns `BigInt` session_id to caller.
2. **`Intake.tsx` discards returned `session_id`** — Now captures `await ensureSessionPersisted()` result and assigns `observer.session_id`.

### HIGH — FIXED
3. **`Sidebar.tsx` observer_id type inconsistent** — Typed as `string` but schema is `bigint`; now imports `Observer` type from `identity.ts`.
4. **`Sidebar.tsx` duplicate observer ID display block** — Removed duplicate `<span>` that rendered same info twice.

### HIGH — FIXED (Commit: subsequent)
5. **No React Error Boundary** — Added `ErrorBoundary` class component wrapping `<SessionProvider>` in `App.tsx`.

---

## Phase 3: Remaining Audit Findings (NOT YET FIXED — next session)

### HIGH (schema change needed — user will handle)
6. **`session_log.user_name` vs `observer.observer_name` naming drift** — DB column is `user_name`, but everywhere else it's `observer_name`. Schema change required.

### MEDIUM
7. **`Settings.tsx` deleteConfirm typed as `any`** — Should be strongly typed union.
8. **Settings delete confirmation ambiguous** — Shows `observer_name` as delete target but doesn't clarify what's being deleted (observer vs species vs stage).
9. **`Login.tsx` double-fetches observer table** — Fetches once for PIN validation, then again for display list. Could cache or combine.
10. **`useVersion` singleton pattern is correct** — Already optimized with module-level cache; no fix needed.
11. **Direct `localStorage` reads in `Sidebar.tsx`** — Minor, but could migrate to context.

### LOW
12. **No Firebase references found** — Not an issue.

---

## E2E Test Coverage Gap Analysis

**Total matrix IDs:** 26  
**Implemented:** ~14 (54%)  
**Missing:** 12

### HIGHEST PRIORITY MISSING (should write first):
- **TC-OBS-008** — Soft-delete cascade verification (DB audit)
- **TC-OBS-009** — Soft-deleted observations excluded from Reports
- **TC-SET-007** — Settings observer CRUD persistence
- **TC-SET-008** — Soft-delete observer exclusion in login list
- **TC-DASH-003** — Dashboard welcome observer_name display
- **TC-INT-005** — Intake session_id association (critical for Phase 2 fix verification)

### QA GOVERNANCE NOTE:
All future tests should follow the **Triad Dispatch pattern**:
- **A0-PM** → triage & task
- **A1-UI Scripter** → write Playwright test ✅
- **A2-DB Auditor** → verify DB state post-test ✅
- **A3-Obsidian** → log results / breadcrumb

---

## Schema Reference — `observer` table (CURRENT)

```sql
CREATE TABLE public.observer (
  observer_name text NOT NULL,              -- WAS display_name; renamed
  is_active boolean NULL DEFAULT true,
  created_at timestamp with time zone NULL DEFAULT now(),
  modified_at timestamp with time zone NULL DEFAULT now(),
  observer_id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  CONSTRAINT observer_pkey PRIMARY KEY (observer_id),
  CONSTRAINT observer_observer_name_key UNIQUE (observer_name)
);
```

## Schema Reference — `session_log` table (NOTE: `user_name` column)

```sql
-- session_log still has user_name column (drift from observer.observer_name)
CREATE TABLE public.session_log (
  session_id bigint GENERATED ALWAYS AS IDENTITY,
  user_name text,                           -- ⚠️ INCONSISTENT — should be observer_name
  login_timestamp timestamptz,
  logout_timestamp timestamptz,
  user_agent text,
  ...
);
```

---

## Clean Chat Handoff Instructions

1. Start from this breadcrumb — all Phase 1-2 changes are committed.
2. Phase 3 items are documented above; prioritize the MEDIUM items (Settings.tsx typing/UX).
3. Schema change for `session_log.user_name` → `observer_name` must be done in Supabase SQL Editor FIRST, then update `Login.tsx` and `identity.ts` references.
4. E2E test gaps: write TC-OBS-008 first (soft-delete cascade) as it verifies Phase 2 session_id fix.
5. Run existing E2E suite to confirm no regressions before writing new tests.
6. Use triad dispatch pattern for all new work.
