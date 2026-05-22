# 🍞 Breadcrumb — Fresh Chat Resume Point

**Date:** 2026-05-22 13:16 CT
**Branch:** `feature/react-resurrection`
**Last Commit:** `e8b384f` — `feat(admin): lookup table CRUD with mid-season lockout and soft-delete [v9.7.2]`

---

## 📋 Current State

### What's Done (Sprint 6)
| Commit | Description |
|--------|-------------|
| `2d18a46` | C1 — Key rotation: SERVICE_ROLE → anon key |
| `6e08962` | H1/M5/M7/M8 — Atomic observations, real observer from DB, live dashboard |
| `b5be8cb` | React hydration crash fix (observer_id bigint→string) |
| `5f0f236` | TypeScript build fix (unused saving/saveError variables) |
| `4609cbc` | Test hardening (retry loops, to_be_attached) |
| `5050b72` | Governance — Ledger update + Obsidian Sprint 6 log |
| `e8b384f` | **LOOKUP TABLE CRUD** — Settings.tsx tabs for Species, Stages, Bio-Props, Observers |

### What's Pending (NEXT TASK)
**🔐 AUTHENTICATION GATE — Prevent unauthorized public access**

The user asked:
> "How does it handle user login now? It was hard coded to me during testing. What is best way to prevent unauth public from using the system?"

Current login is **wide open** — no login screen, the `SessionContext` loads observers from DB (falls back to `Kevin (Audit Override)` if DB is empty). Anyone who reaches the URL can use the app.

**Recommended approach (user agreed):**
1. **Create `Login.tsx` page** — PIN entry (4-6 digit PIN stored in `system_config` as `AUTH_PIN`)
2. **Observer selection** — after PIN validation, user selects observer from DB list
3. **Session logging** — log to `session_log` per §4 forensic auditing
4. **Remove KEVIN_BYPASS in production** — only in dev mode
5. **Tighten RLS policies** — require `auth.role() = 'authenticated'` on clinical tables

**User's security concern:** "Token is required to be exposed during front end execution?? Can we assign a variable so public can't hack it?"
- The anon key IS publicly visible by design — Supabase uses RLS for security, not key secrecy
- Service role key already rotated to anon (C1 commit). Security comes from RLS + login gate.

---

## 🔗 Key Paths

| What | Path |
|------|------|
| React frontend source | `/a0/usr/workdir/frontend/src/` |
| Settings (CRUD admin) | `/a0/usr/workdir/frontend/src/pages/Settings.tsx` (704 lines) |
| Session context | `/a0/usr/workdir/frontend/src/context/SessionContext.tsx` |
| Supabase client | `/a0/usr/workdir/frontend/src/lib/supabase.ts` |
| Version hook | `/a0/usr/workdir/frontend/src/hooks/useVersion.ts` |
| Database migrations | `/a0/usr/workdir/supabase_db/migrations/` |
| QA Triad Ledger | `/a0/usr/workdir/tests/QA_TRIAD_LEDGER.md` |
| Sprint 6 obsidian log | `/a0/usr/workdir/obsidian/Sprint_6_Completion_20260522.md` |
| Latest migration (v9.7.2) | `/a0/usr/workdir/supabase_db/migrations/v9_7_2_LOOKUP_SOFT_DELETE.sql` |
| Requirements | `/a0/usr/workdir/docs/design/Requirements.md` |
| Implied objective | `/a0/usr/workdir/docs/implied_system_objective.md` |
| Frontend .env | `/a0/usr/workdir/frontend/.env` |
| Production build | `/a0/usr/workdir/frontend/dist/` |
| Vite dev server | Running on `172.18.0.3:5173` (--host 0.0.0.0) |
| Streamlit | Running on `127.0.0.1:8599` (deprecated) |

---

## 🚨 Gotchas for Fresh Agent

1. **Streamlit is DEPRECATED** — React is the sole target. All Streamlit tests marked `[DEPRECATED_STREAMLIT]` in Ledger.
2. **observer_id is BIGINT in DB** — must convert to string before `.slice()` in Sidebar, or React crashes silently.
3. **All deletes are SOFT DELETES** — use `UPDATE SET is_deleted=true`. Never call `.delete()`.
4. **Mid-season lockout** — Settings CRUD page queries active egg count; disables edits if >0.
5. **Version sovereignty** — version comes from `system_config.APP_VERSION` (currently v9.7.2). Update test when version changes.
6. **Use sub-agents for complex tasks** — per orchestration rules in `subagent.promptinclude.md`.
7. **Log bugs to Obsidian** — per QA Methodology in `qa.promptinclude.md`.

---

## 🚦 Next Step for Fresh Agent

**Implement Login Gate (Auth System):**
1. Create `Login.tsx` page with PIN entry
2. Add `AUTH_PIN` to `system_config` table
3. Update `SessionContext` to require authentication
4. Route to login page by default; redirect to Dashboard on success
5. Log sessions to `session_log`
6. Remove hardcoded KEVIN_BYPASS in production (keep for dev mode)
7. Verify RLS policies on clinical tables
8. Run `npm run build` to verify zero TS errors

**The user wants to switch to a fresh chat. They are waiting for confirmation that I'm ready.**
