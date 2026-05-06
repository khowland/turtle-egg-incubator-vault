# Bug-SCHEMA-001—004: Schema Migration Gaps Resolution

**Date:** 2026-05-05 20:37 CT
**Resolved by:** Kevin Howland (manual SQL execution)
**Status:** RESOLVED ✅

---

## Summary

Four schema migration gaps were identified via live runtime log analysis and the `Schema_Drift_Audit_v920.md`. These gaps blocked intake saves and session logging at the application level. All four were resolved by Kevin via direct SQL execution in the Supabase SQL Editor.

---

## Resolved Issues

| Bug ID | CR ID | Table | Missing Column | Runtime Error | Fix Applied |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bug-SCHEMA-001** | CR-P0-01 | `bin_observation` | `observer_id` (uuid) | `column "observer_id" of relation "bin_observation" does not exist` — blocked all intake saves via `vault_finalize_intake` RPC | `ALTER TABLE bin_observation ADD COLUMN observer_id uuid;` + FK constraint |
| **Bug-SCHEMA-002** | CR-P0-02 | `session_log` | `modified_at` (timestamptz) | `record "new" has no field "modified_at"` — blocked session_log INSERT on every login | `ALTER TABLE session_log ADD COLUMN modified_at timestamptz DEFAULT now();` + backfill |
| **Bug-SCHEMA-003** | CR-P1-02 | `bin_observation` | `created_at` (timestamptz) | No runtime error — forensic gap per Mandatory Audit Column Standard | `ALTER TABLE bin_observation ADD COLUMN created_at timestamptz DEFAULT now();` + backfill |
| **Bug-SCHEMA-004** | CR-P1-02 | `egg_observation` | `created_at` (timestamptz) | No runtime error — forensic gap per Mandatory Audit Column Standard | `ALTER TABLE egg_observation ADD COLUMN created_at timestamptz DEFAULT now();` + backfill |

---

## SQL Executed (Kevin)

```sql
-- Bug-SCHEMA-001: Unblocks ALL intake saves
ALTER TABLE public.bin_observation ADD COLUMN observer_id uuid;
ALTER TABLE public.bin_observation ADD CONSTRAINT fk_bin_observation_observer FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);

-- Bug-SCHEMA-002: Fixes session logging errors
ALTER TABLE public.session_log ADD COLUMN modified_at timestamptz DEFAULT now();
UPDATE public.session_log SET modified_at = login_timestamp WHERE modified_at IS NULL;

-- Bug-SCHEMA-003: Forensic gap — bin_observation created_at
ALTER TABLE public.bin_observation ADD COLUMN created_at timestamptz DEFAULT now();
UPDATE public.bin_observation SET created_at = COALESCE(timestamp, modified_at) WHERE created_at IS NULL;

-- Bug-SCHEMA-004: Forensic gap — egg_observation created_at
ALTER TABLE public.egg_observation ADD COLUMN created_at timestamptz DEFAULT now();
UPDATE public.egg_observation SET created_at = egg_observation_date WHERE created_at IS NULL;
```

---

## Impact

| Metric | Before | After |
| :--- | :--- | :--- |
| Intake SAVE success rate | 0% (blocked by RPC error) | Should be 100% (pending verification) |
| Session log writes | Failing on every login | Should succeed |
| Audit trail completeness | bin_observation/egg_observation missing creation timestamps | Now tracked |
| Tests unblocked | ~30 intake-dependent tests failing | Should be runnable |

---

## Verification

- [ ] Create a new intake via UI and confirm no `400 Bad Request` on RPC call
- [ ] Confirm session_log rows now include `modified_at`
- [ ] Confirm `bin_observation` and `egg_observation` rows include `created_at` on next insert

---

*Resolution recorded per QA Methodology Mandatory Reporting standard.*
