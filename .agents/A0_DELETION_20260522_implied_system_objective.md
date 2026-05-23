# A0 Delegation: Update `implied_system_objective.md`

**Issued by**: Agent Zero supervisor (user directive)
**Date**: 2026-05-22
**Priority**: HIGH
**Related CR**: `change_request_20260522_schema_extend_session_fix.txt`

## Task

Update `docs/implied_system_objective.md` to reflect current system reality.

## Key Changes Required

1. **Streamlit deprecated**: All references to Streamlit, `st.`, `streamlit run`, or Streamlit UI patterns must be removed or marked as DEPRECATED.
2. **React/TypeScript frontend is sole UI**: The frontend lives in `frontend/`, built with Vite, served via `npm run build` / `npm run dev`.
3. **Authentication**: Switch from local login/password to **Google OAuth via Supabase Auth**. The `Login.tsx` page triggers `supabase.auth.signInWithOAuth({ provider: 'google' })`.
4. **Version bump**: Current version is now v9.8.x (was v8.2.0).
5. **Session persistence bug**: Document that `session_id` in `session_log` is `GENERATED ALWAYS AS IDENTITY` but `identity.ts` attempts manual INSERT — this mismatch causes the "Forensic session persistence failure" critical error.
6. **Schema changes**: Remove `days_in_care`; add `disp_date` (date) and `scl` (numeric) to the objectives.
7. **RLS**: Document that RLS policies are enabled on all clinical tables (v9.7.0+).
8. **Knowledge management**: Cross-reference `/obsidian/` as the canonical knowledge base (not just implied — explicit).

## Inventory of Inconsistencies to Fix

| Old Content | Reality |
|:---|:---|
| "Streamlit-based single-page app" | React SPA with routing |
| "Local login with password" | Google OAuth via Supabase Auth |
| "session_id is bigint manually assigned" | `GENERATED ALWAYS AS IDENTITY` (PK migration v9.1.0) |
| "Days in Care numeric field" | Being replaced by `disp_date` (date) + `scl` (numeric) |
| "app.py is the entry point" | `frontend/src/main.tsx` is the entry point |
| "No RLS" | RLS enabled on all clinical tables since v9.7.0 |

## Do Not Change

- Core biological model (S0-S6 stages, species, incubation parameters)
- Soft delete policy
- Clinical visibility (global, not per-observer)
- Session persistence 1-hour window
- Forensic audit trail requirements

## Verification

After update, the document should be factually correct for a developer who has never seen the codebase. If any statement would mislead them, it needs fixing.

## Output

Write the updated file directly. No new file — overwrite `docs/implied_system_objective.md`.
