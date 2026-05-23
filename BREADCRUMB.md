# 🍞 Breadcrumb — Fresh Chat Resume Point

**Date:** 2026-05-22 16:12 CT
**Branch:** `feature/react-resurrection`
**Last Commit:** `d63c739` — `feat(auth): Add anonymous sign-in to Login.tsx for authenticated JWT [v9.8.0]`

---

## 📋 Current State

### What's Done (Sprint 6 + Login Gate)

| Commit | Description |
|--------|-------------|
| `2d18a46` | C1 — Key rotation: SERVICE_ROLE → anon key |
| `6e08962` | H1/M5/M7/M8 — Atomic observations, real observer from DB, live dashboard |
| `b5be8cb` | React hydration crash fix (observer_id bigint→string) |
| `5f0f236` | TypeScript build fix (unused saving/saveError variables) |
| `4609cbc` | Test hardening (retry loops, to_be_attached) |
| `5050b72` | Governance — Ledger update + Obsidian Sprint 6 log |
| `e8b384f` | **LOOKUP TABLE CRUD** — Settings.tsx tabs for Species, Stages, Bio-Props, Observers |
| `bb42a5e` | **🔐 LOGIN GATE** — PIN auth, Login.tsx, SessionContext, App.tsx guard, RLS tighten, verify_pin RPC |
| `d63c739` | **🔐 ANONYMOUS AUTH** — supabase.auth.signInAnonymously() gives JWT with authenticated role |

### ✅ Login Gate — Complete

- **Login page:** `Login.tsx` with PIN entry (6-digit, masked) + observer selector
- **SessionContext:** `isAuthenticated`, `login()`, `logout()`, dev mode auto-bypass (`VITE_DEV_MODE=true`)
- **App.tsx:** Route guard — shows Login until authenticated
- **Database:** 
  - `v9_8_0_LOGIN_GATE.sql` — AUTH_PIN seed + verify_pin RPC (SECURITY DEFINER)
  - `v9_8_1_RLS_SELECT_AUTH.sql` — Clinical SELECT restricted to authenticated role
- **Auth flow:** PIN → verify_pin RPC → observer selection → signInAnonymously() → JWT (authenticated role) → session_log insert → Dashboard
- **Default PIN:** `123456` (change in Supabase → system_config → AUTH_PIN)
- **Anonymous Auth:** Enabled in Supabase Dashboard (Authentication → Configuration → Sign In / Providers)

### 🟡 Remaining / Next Steps

| Priority | Task |
|----------|------|
| High | **Change default PIN** to a strong value in production system_config |
| High | **Set VITE_DEV_MODE=false** and rebuild for production deployment |
| Medium | **Add brute-force protection** to verify_pin RPC (attempt tracking + lockout) |
| Medium | **Session persistence** — remember auth across page refreshes |
| Low | Logout button in UI |

---

## 🔗 Key Paths

| What | Path |
|------|------|
| React frontend source | `/a0/usr/workdir/frontend/src/` |
| Login page | `/a0/usr/workdir/frontend/src/pages/Login.tsx` (161 lines) |
| Settings (CRUD admin) | `/a0/usr/workdir/frontend/src/pages/Settings.tsx` (704 lines) |
| Session context | `/a0/usr/workdir/frontend/src/context/SessionContext.tsx` |
| Supabase client | `/a0/usr/workdir/frontend/src/lib/supabase.ts` |
| Identity types | `/a0/usr/workdir/frontend/src/lib/identity.ts` |
| Database migrations | `/a0/usr/workdir/supabase_db/migrations/` |
| PIN verify RPC | `/a0/usr/workdir/supabase_db/migrations/v9_8_0_LOGIN_GATE.sql` |
| RLS select auth | `/a0/usr/workdir/supabase_db/migrations/v9_8_1_RLS_SELECT_AUTH.sql` |
| Frontend .env | `/a0/usr/workdir/frontend/.env` |
| Production build | `/a0/usr/workdir/frontend/dist/` |
| Vite dev server | Running on `172.18.0.3:5173` (--host 0.0.0.0) |
| Requirements | `/a0/usr/workdir/docs/design/Requirements.md` |

---

## 🚨 Gotchas for Fresh Agent

1. **Streamlit is DEPRECATED** — React is the sole target.
2. **observer_id is BIGINT in DB** — must convert to string before `.slice()` in Sidebar.
3. **All deletes are SOFT DELETES** — use `UPDATE SET is_deleted=true`. Never call `.delete()`.
4. **Mid-season lockout** — Settings CRUD page queries active egg count; disables edits if >0.
5. **Version sovereignty** — version from `system_config.APP_VERSION` (currently v9.8.0).
6. **Anonymous auth** — supabase.auth.signInAnonymously() provides JWT for authenticated role.
7. **Anon key is public** — security relies on RLS + login gate, NOT key secrecy.
8. **Use sub-agents for complex tasks** — per orchestration rules.
9. **Log bugs to Obsidian** — per QA Methodology.

---

## 🚦 Next Step for Fresh Agent

**The login gate is complete.** Next priority is preparing for public deployment:
1. Change default PIN in Supabase system_config
2. Set VITE_DEV_MODE=false in frontend/.env
3. Run npm run build for production
4. Add brute-force protection to verify_pin RPC
5. Consider session persistence (localStorage token)