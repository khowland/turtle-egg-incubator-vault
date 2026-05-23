# Google OAuth Implementation Plan &amp; Impact Assessment
**Date:** 2026-05-23  
**Status:** PLANNING — NO CODE CHANGES  
**Author:** Triad Dispatch (QA Auditor + React Expert + Supervisor)

---

## Executive Summary

**Current State:** The WINC Turtle Incubation System uses a 4-digit PIN lookup
against the `observer` table (local auth), backed by `supabase.auth.signInAnonymously()`
for the Supabase Auth layer. There is no connection between the Observer record and
the Supabase Auth user.

**Target State:** Observers authenticate via Google OAuth (Gmail accounts). The
Supabase Auth user (`auth.users`) maps 1:1 to the Observer record. Session tracking
(`session_log`) and RLS policies align to `auth.uid()`, removing anonymous auth.

**Risk Level:** HIGH — Touches every page, every RLS policy, and the entire
session lifecycle. Requires database migration and coordinated deploy.

---

## 1. Current Architecture (As-Is)

```
┌─────────────────────────────────────────────────────────────────┐
│                        WINC AUTH FLOW (v9.8.x)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Login.tsx]                                                     │
│    │                                                             │
│    ├─ 1. User enters 4-digit PIN                                 │
│    ├─ 2. SELECT observer WHERE observer_id = PIN                 │
│    ├─ 3. supabase.auth.signInAnonymously() ← NO user identity    │
│    ├─ 4. INSERT session_log (observer_name, user_agent, ...)     │
│    ├─ 5. ensureSessionPersisted() → localStorage                 │
│    └─ 6. Navigate to /dashboard                                  │
│                                                                  │
│  [SessionContext.tsx]                                             │
│    └─ Holds { observer_id, observer_name, session_id } in React  │
│                                                                  │
│  [App.tsx]                                                        │
│    └─ On mount: restoreSessionFromPersistence() → validate via   │
│       SELECT session_log WHERE session_id = storedId             │
│                                                                  │
│  [identity.ts]                                                    │
│    └─ ensureSessionPersisted(supabase, observer)                  │
│       └─ localStorage.setItem('session', JSON.stringify(...))    │
│                                                                  │
│  RLS POLICIES:                                                    │
│    └─ USING (true) — NO user-based filtering                     │
│                                                                  │
│  PROBLEMS:                                                        │
│    • Anonymous auth = no user identity for RLS                    │
│    • PIN is static, shareable, not auditable per-user              │
│    • No MFA, no session timeout, no token refresh                 │
│    • localStorage session can be forged                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Target Architecture (To-Be)

```
┌─────────────────────────────────────────────────────────────────┐
│                    WINC AUTH FLOW (Google OAuth)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [Login.tsx]                                                     │
│    │                                                             │
│    ├─ 1. User clicks "Sign in with Google"                       │
│    ├─ 2. supabase.auth.signInWithOAuth({ provider: 'google' })   │
│    ├─ 3. Supabase creates/updates auth.users row                 │
│    ├─ 4. onAuthStateChange fires → we get auth.user.id           │
│    ├─ 5. SELECT observer WHERE auth_user_id = auth.user.id       │
│    ├─ 6. INSERT session_log (auth_user_id, observer_name, ...)   │
│    ├─ 7. SessionContext.login(observer, sessionId)               │
│    └─ 8. Navigate to /dashboard                                  │
│                                                                  │
│  [SessionContext.tsx]                                             │
│    └─ Uses supabase.auth.onAuthStateChange for session restore   │
│                                                                  │
│  [App.tsx]                                                        │
│    └─ Listens to auth state; auto-restores on page reload        │
│                                                                  │
│  RLS POLICIES:                                                    │
│    └─ USING (auth_user_id = auth.uid()) — USER-BASED filtering   │
│                                                                  │
│  BENEFITS:                                                        │
│    • Real Supabase Auth user identity                             │
│    • RLS enforcement per authenticated user                       │
│    • Token-based sessions (refresh, expiry)                       │
│    • Google account = real email identity                         │
│    • Future: Google profile photo in sidebar                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Schema Changes Required

### 3.1 `observer` Table

```sql
-- Add column linking observer to Supabase Auth user
ALTER TABLE public.observer
  ADD COLUMN auth_user_id uuid NULL
  REFERENCES auth.users(id) ON DELETE SET NULL;

-- Unique constraint (one auth user = one observer)
CREATE UNIQUE INDEX idx_observer_auth_user_id
  ON public.observer(auth_user_id)
  WHERE auth_user_id IS NOT NULL;

-- Backfill: NULL for existing observers (grandfathered)
-- Migrate: Admin sets auth_user_id via settings UI later
```

### 3.2 `session_log` Table

```sql
-- Add auth user reference
ALTER TABLE public.session_log
  ADD COLUMN auth_user_id uuid NULL
  REFERENCES auth.users(id) ON DELETE SET NULL;

-- Make observer_name nullable (optional when we have auth_user_id)
ALTER TABLE public.session_log
  ALTER COLUMN observer_name DROP NOT NULL;
```

### 3.3 RLS Policies — ALL Clinical Tables

Every table that currently uses `USING (true)` must be updated:

```sql
-- Current (insecure):
CREATE POLICY "Authenticated users can select" ON public.bin
  FOR SELECT USING (true);

-- Target (per-user):
CREATE POLICY "Users can select own bins" ON public.bin
  FOR SELECT USING (
    auth_user_id = auth.uid()
  );
```

**Tables requiring RLS update (7 tables):**

| Table | Session FK | Migration |
|---|---|---|
| `bin` | `session_id → session_log` | Add `auth_user_id` column |
| `bin_observation` | `session_id → session_log` | Add `auth_user_id` column |
| `egg` | `session_id → session_log` | Add `auth_user_id` column |
| `egg_observation` | `session_id → session_log` | Add `auth_user_id` column |
| `hatchling_ledger` | `session_id → session_log` | Add `auth_user_id` column |
| `intake` | `session_id → session_log` | Add `auth_user_id` column |
| `system_log` | `session_id → session_log` | Add `auth_user_id` column |

**Two strategies for RLS:**

*Strategy A — Denormalize `auth_user_id`* (recommended):
- Add `auth_user_id uuid REFERENCES auth.users(id)` to all 7 tables
- Populate on INSERT from `session_log.auth_user_id`
- RLS: `USING (auth_user_id = auth.uid())`
- ✅ Simple, fast RLS checks
- ❌ 7 schema changes

*Strategy B — JOIN-based RLS:*
- Keep current schema, use subquery in RLS policy
- RLS: `USING (session_id IN (SELECT session_id FROM session_log WHERE auth_user_id = auth.uid()))`
- ✅ No schema changes to clinical tables
- ❌ Every query does a subquery → performance degradation at scale

**Recommendation: Strategy A** for clinical tables that are queried frequently
(observations, bins, eggs). Strategy B acceptable for low-volume tables
(hatchling_ledger, system_log).

---

## 4. Frontend Changes

### 4.1 `Login.tsx` — Complete Rewrite

| Section | Current | Target |
|---|---|---|
| Auth method | 4-digit PIN lookup | Google OAuth button |
| PIN UI | Input field + submit | Replace with "Sign in with Google" button |
| Observer lookup | `SELECT by observer_id = PIN` | `SELECT by auth_user_id = auth.user.id` |
| Session creation | `INSERT session_log (observer_name, ...)` | `INSERT session_log (auth_user_id, observer_name, ...)` |
| Error handling | Invalid PIN message | OAuth cancellation, account not found |
| Loading state | Spinner | Supabase OAuth redirect handling |

**Code structure:**

```typescript
// Login.tsx — Google OAuth version

import { supabase } from '../lib/supabase';

const LoginPage = () => {
  const handleGoogleSignIn = async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            access_type: 'offline',
            prompt: 'consent',
          },
        },
      });

      if (error) {
        console.error('[Login] OAuth error:', error);
        setError('Google sign-in failed. Please try again.');
      }
      // Redirect happens automatically — no manual navigation
    } catch (err) {
      console.error('[Login] Unexpected OAuth error:', err);
      setError('An unexpected error occurred. Please try again.');
    }
  };

  return (
    <button onClick={handleGoogleSignIn}>
      Sign in with Google
    </button>
  );
};
```

### 4.2 New File: `AuthCallback.tsx`

```typescript
// pages/AuthCallback.tsx
// Handles OAuth redirect, links auth user to observer, creates session

const AuthCallback = () => {
  useEffect(() => {
    supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        // 1. Look up observer by auth_user_id
        const { data: observer } = await supabase
          .from('observer')
          .select('*')
          .eq('auth_user_id', session.user.id)
          .is('is_deleted', false)
          .single();

        if (!observer) {
          // 2. No observer linked — show "request access" screen
          setError('No observer account found for this Google account.');
          return;
        }

        // 3. Create session_log
        const { data: sessionEntry } = await supabase
          .from('session_log')
          .insert({
            auth_user_id: session.user.id,
            observer_name: observer.observer_name,
            user_agent: navigator.userAgent,
            login_timestamp: new Date().toISOString(),
          })
          .select('session_id')
          .single();

        // 4. Set context + navigate
        login(observer, sessionEntry.session_id);
        navigate('/dashboard');
      }
    });
  }, []);
};
```

### 4.3 `SessionContext.tsx` — Refactor

| Change | Detail |
|---|---|
| Remove Kevin bypass | Dev mode uses Google OAuth mock instead |
| Add `onAuthStateChange` listener | Auto-restore session on page reload |
| Remove localStorage persistence | Supabase handles token persistence |
| Add `authUser` to context | `authUser: User \| null` from Supabase |
| Add `signOut` | `supabase.auth.signOut()` |

### 4.4 `App.tsx` — Add Auth Listener

```typescript
// App.tsx — Add at top level

useEffect(() => {
  const { data: { subscription } } = supabase.auth.onAuthStateChange(
    async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        // Restore observer from DB
        const { data: observer } = await supabase
          .from('observer')
          .select('*')
          .eq('auth_user_id', session.user.id)
          .single();

        if (observer) {
          // Create new session or restore existing
          // ...
        }
      } else if (event === 'SIGNED_OUT') {
        logout();
      }
    }
  );

  return () => subscription.unsubscribe();
}, []);
```

### 4.5 `identity.ts` — Deprecate

| Component | Action |
|---|---|
| `ensureSessionPersisted()` | ❌ REMOVE — Supabase handles token persistence |
| `restoreSessionFromPersistence()` | ❌ REMOVE — onAuthStateChange restores session |
| `Observer` interface | Add `auth_user_id?: string` field |

### 4.6 `Sidebar.tsx`

| Current | Target |
|---|---|
| `observer.observer_name` display | `observer.observer_name` (unchanged) |
| Logout calls `logout()` | Logout calls `supabase.auth.signOut()` |
| No user avatar | Google profile photo from `session.user.user_metadata.avatar_url` |

### 4.7 `Settings.tsx` — Observer Management

| Current | Target |
|---|---|
| CRUD on observer (name, active) | Add "Link Google Account" button per observer |
| Add new observer | Obserers created without auth_user_id (pending link) |
| Delete observer | Sets `is_deleted` + clears `auth_user_id` |

---

## 5. Supabase Configuration

### 5.1 Google Cloud Console

1. Create OAuth 2.0 Client ID in Google Cloud Console
2. Set Authorized JavaScript origins: `https://[project-ref].supabase.co`
3. Set Authorized redirect URIs: `https://[project-ref].supabase.co/auth/v1/callback`
4. Add test users (email allowlist during development)

### 5.2 Supabase Dashboard

1. **Authentication → Providers → Google:** Enabled
2. Enter Client ID and Client Secret from Google Cloud Console
3. **Authentication → Settings → Site URL:** Production URL
4. **Authentication → Settings → Redirect URLs:** Add localhost for dev

### 5.3 Environment Variables (`.env` + Supabase)

```env
# Supabase project config (existing)
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...

# Google OAuth (new)
VITE_GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
```

---

## 6. Migration Strategy

### Phase 1: Coexistence (Week 1)
- Deploy schema changes (3.1, 3.2) — backward compatible
- Add `auth_user_id` column to observer (nullable)
- Add `auth_user_id` column to session_log (nullable)
- Deploy new Login.tsx with BOTH Google + PIN options
- `auth_user_id` defaults to NULL → existing PIN login still works

### Phase 2: Admin Link (Week 1-2)
- Settings page: Admin links existing observers to Google accounts
- SQL: `UPDATE observer SET auth_user_id = 'uuid' WHERE observer_id = X`
- Test: Linked observers can use Google sign-in

### Phase 3: Full Cutover (Week 2)
- Remove PIN login from Login.tsx
- Add RLS policies (Strategy A for high-traffic tables)
- Remove `signInAnonymously()` from codebase
- Remove localStorage session persistence

### Phase 4: Hardening (Week 3)
- Enforce NOT NULL on `auth_user_id` in observer table
- Enforce NOT NULL on `auth_user_id` in session_log
- Row-Level Security audit (verify all 7 tables)
- E2E tests with real Google accounts

---

## 7. Impact Assessment

### 7.1 Files Changed (16 files)

| File | Impact | Effort |
|---|---|---|
| `Login.tsx` | Complete rewrite | HIGH |
| `AuthCallback.tsx` | NEW file | MEDIUM |
| `SessionContext.tsx` | Refactor (remove Kevin bypass) | MEDIUM |
| `App.tsx` | Add auth listener | LOW |
| `identity.ts` | Deprecate localStorage functions | LOW |
| `Sidebar.tsx` | Google avatar, signOut | LOW |
| `Settings.tsx` | Add auth_user_id management | MEDIUM |
| `Intake.tsx` | `auth_user_id` in session | LOW |
| `Observations.tsx` | `auth_user_id` in session | LOW |
| `Dashboard.tsx` | `auth_user_id` query filter | LOW |
| **SQL migration** | Schema changes (observer, session_log, 7 clinical tables) | HIGH |
| **RLS policies** | 7 tables — drop `USING (true)`, add per-user | HIGH |
| **Supabase config** | Google provider, redirect URIs | MEDIUM |
| **Google Cloud** | OAuth 2.0 client, consent screen | MEDIUM |
| **E2E tests** | Auth flow rewrite | HIGH |
| **`.env`** | New env vars | LOW |

### 7.2 Breaking Changes

| Break | Mitigation |
|---|---|
| PIN login removed | Coexistence period (Phase 1-2) |
| RLS `USING (true)` removed | Gradual policy deployment |
| `signInAnonymously()` removed | Coexistence period |
| localStorage session removed | `onAuthStateChange` listener |
| Kevin dev bypass removed | Google OAuth test accounts for dev |
| `observer_name` nullable in session_log | Backward-compatible migration |

### 7.3 Rollback Plan

1. **Schema rollback (safe):** `auth_user_id` is nullable — zero data loss
2. **RLS rollback:** Re-apply `USING (true)` policies (archived in migration)
3. **Frontend rollback:** Revert Login.tsx to PIN-only version (git tag)
4. **Supabase rollback:** Disable Google provider in dashboard

### 7.4 Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Observer not linked to Google account | HIGH | User locked out | Coexistence period + admin link UI |
| RLS breaks existing queries | MEDIUM | Data invisible | Staged RLS rollout per table |
| OAuth redirect fails in iframe | LOW | Sign-in broken | Supabase popup mode fallback |
| Token refresh fails | LOW | Mid-session logout | Graceful re-auth prompt |
| Google Cloud quota exceeded | LOW | Sign-in throttled | Monitor in GCP console |
| Session_log migration breaks inserts | LOW | Cannot log in | Backward-compatible schema |

---

## 8. Testing Requirements

### 8.1 Unit Tests (New)

- `test_oauth_callback_success` — Observer found, session created
- `test_oauth_callback_observer_not_found` — Error screen shown
- `test_oauth_callback_observer_deleted` — Soft-delete check
- `test_session_restore_on_reload` — onAuthStateChange fires
- `test_sign_out_clears_context` — logout called, session cleared
- `test_rls_policy_enforces_auth_user` — Can't see other users' bins

### 8.2 E2E Tests (Updated)

- `TC-LOGIN-001` — Google sign-in happy path
- `TC-LOGIN-002` — Observer not linked
- `TC-LOGIN-003` — Token refresh mid-session
- `TC-LOGIN-004` — Sign out + re-sign-in
- `TC-OBS-008` — Soft-delete cascade with auth (existing gap)

### 8.3 Security Tests

- Verify RLS prevents cross-user data access
- Verify session_log.auth_user_id is never NULL after Phase 4
- Verify Supabase anon key doesn't leak in frontend bundle
- Verify OAuth state parameter prevents CSRF

---

## 9. Implementation Timeline

| Week | Milestone | Deliverables |
|---|---|---|
| **Week 1** | Schema + coexistence | SQL migration, Login.tsx with dual auth, AuthCallback.tsx |
| **Week 2** | Cutover + RLS | Remove PIN, add RLS policies, admin link UI |
| **Week 3** | Hardening + tests | NOT NULL constraints, E2E tests, security audit |
| **Week 4** | Buffer | Bug fixes, performance tuning, rollback drill |

---

## 10. Open Questions

1. **Observer provisioning:** Who creates observer accounts? Will we build a self-registration flow or keep admin-managed?
2. **Google Workspace domain restriction:** Should we restrict to `@wisc.edu` or `@winc.org` domains only?
3. **Offline mode:** Current PIN auth works offline (local lookup). Google OAuth requires internet. Acceptable?
4. **Multi-device sessions:** Should we allow concurrent sessions per observer?
5. **Session timeout:** Should sessions expire after N hours of inactivity? (Supabase supports JWT expiry config)
6. **Google profile data:** Should we store `avatar_url`, `full_name`, `email` in the observer table?

---

## Appendix A: Supabase Auth JavaScript API Reference

```typescript
// Sign in
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'https://example.com/auth/callback',
  },
});

// Listen for auth changes
supabase.auth.onAuthStateChange((event, session) => {
  console.log(event, session);
});

// Get current session
const { data: { session } } = await supabase.auth.getSession();

// Sign out
const { error } = await supabase.auth.signOut();

// Get user
const { data: { user } } = await supabase.auth.getUser();
```

## Appendix B: RLS Policy Template

```sql
-- Before (current):
CREATE POLICY "Allow all" ON public.bin
  FOR SELECT USING (true);

-- After (Strategy A):
ALTER TABLE public.bin ADD COLUMN auth_user_id uuid REFERENCES auth.users(id);
CREATE POLICY "Users see own bins" ON public.bin
  FOR SELECT USING (auth_user_id = auth.uid());

-- After (Strategy B):
CREATE POLICY "Users see own bins" ON public.bin
  FOR SELECT USING (
    session_id IN (
      SELECT session_id FROM public.session_log
      WHERE auth_user_id = auth.uid()
    )
  );
```
