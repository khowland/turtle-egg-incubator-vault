# Schema Drift Audit — v9.2.0

**Audit Date**: 2026-05-04 16:39 CDT  
**Database**: `kxfkfeuhkdopgmkpdimo.supabase.co` (PostgREST REST API)  
**Source**: `information_schema.columns` (via OpenAPI introspection) + `system_config` query  
**Auditor**: Agent Zero DB Auditor (A2-DB)

---

## Current App Version

| Config Key  | Config Value |
|-------------|-------------|
| `APP_VERSION` | `v9.2.0` |

---

## Mandatory Audit Column Standard

Per `SYSTEM_DESIGN_SPEC.md`, **all transactional tables** MUST include these six audit columns:

| # | Column Name   | Expected Type         | Notes                               |
|---|---------------|-----------------------|-------------------------------------|
| 1 | `session_id`   | `TEXT`                |                                     |
| 2 | `created_at`   | `TIMESTAMPTZ`         |                                     |
| 3 | `modified_at`  | `TIMESTAMPTZ`         |                                     |
| 4 | `created_by_id`| `UUID`                | FK → `observer.observer_id`         |
| 5 | `modified_by_id`| `UUID`               | FK → `observer.observer_id`         |
| 6 | `is_deleted`   | `BOOLEAN`             | Soft-delete flag                    |

---

## Per-Table Audit Results

### ✅ FULLY COMPLIANT

| Table              | Status  | Notes |
|--------------------|---------|-------|
| `intake`           | **PASS** | All 6 audit columns present with correct types |
| `bin`              | **PASS** | All 6 audit columns present with correct types |
| `egg`              | **PASS** | All 6 audit columns present with correct types |

---

### ❌ DRIFT DETECTED (Missing Columns)

#### 1. `bin_observation` — Missing `created_at`

| Missing Column | Expected Type |
|----------------|---------------|
| `created_at`   | `TIMESTAMPTZ` |

**Existing audit columns**: `session_id` ✅, `modified_at` ✅, `created_by_id` ✅, `modified_by_id` ✅, `is_deleted` ✅  
**Gap**: No creation timestamp exists; observation creation time is untrackable. Row audit trail is incomplete.

```sql
-- Remediation:
ALTER TABLE bin_observation ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
-- Backfill from modified_at or timestamp:
UPDATE bin_observation SET created_at = COALESCE(timestamp, modified_at) WHERE created_at IS NULL;
ALTER TABLE bin_observation ALTER COLUMN created_at SET NOT NULL;
```

---

#### 2. `egg_observation` — Missing `created_at`

| Missing Column | Expected Type |
|----------------|---------------|
| `created_at`   | `TIMESTAMPTZ` |

**Existing audit columns**: `session_id` ✅, `modified_at` ✅, `created_by_id` ✅, `modified_by_id` ✅, `is_deleted` ✅  
**Gap**: Same issue as `bin_observation` — no record creation timestamp.

```sql
-- Remediation:
ALTER TABLE egg_observation ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
-- Backfill from egg_observation_date:
UPDATE egg_observation SET created_at = egg_observation_date WHERE created_at IS NULL;
ALTER TABLE egg_observation ALTER COLUMN created_at SET NOT NULL;
```

---

#### 3. `hatchling_ledger` — Missing `created_by_id`, `modified_by_id`

| Missing Column    | Expected Type |
|-------------------|---------------|
| `created_by_id`   | `UUID`        |
| `modified_by_id`  | `UUID`        |

**Existing audit columns**: `session_id` ✅, `created_at` ✅, `modified_at` ✅, `is_deleted` ✅  
**Gap**: No user/organization attribution for creation or modification events.

```sql
-- Remediation:
ALTER TABLE hatchling_ledger ADD COLUMN created_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE hatchling_ledger ADD COLUMN modified_by_id UUID REFERENCES observer(observer_id);
```

---

#### 4. `session_log` — Missing 5 of 6 audit columns

| Missing Column    | Expected Type |
|-------------------|---------------|
| `created_at`      | `TIMESTAMPTZ` |
| `modified_at`     | `TIMESTAMPTZ` |
| `created_by_id`   | `UUID`        |
| `modified_by_id`  | `UUID`        |
| `is_deleted`      | `BOOLEAN`     |

**Existing audit columns**: `session_id` ✅  
**Gap**: Session log table lacks nearly all audit infrastructure. Currently has: `login_timestamp`, `session_id`, `user_agent`, `user_name`.

**Assessment**: `session_log` may be append-only and `created_at` may be served by `login_timestamp`. However, the spec mandates all 6 columns. Consider whether this table is truly "transactional" or if it's a log stream where soft-delete and modification tracking don't apply.

```sql
-- Remediation (if needed):
ALTER TABLE session_log ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE session_log ADD COLUMN modified_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE session_log ADD COLUMN created_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE session_log ADD COLUMN modified_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE session_log ADD COLUMN is_deleted BOOLEAN DEFAULT false;
```

---

#### 5. `observer` — Missing 4 of 6 audit columns

| Missing Column    | Expected Type |
|-------------------|---------------|
| `session_id`      | `TEXT`        |
| `created_by_id`   | `UUID`        |
| `modified_by_id`  | `UUID`        |
| `is_deleted`      | `BOOLEAN`     |

**Existing audit columns**: `created_at` ✅, `modified_at` ✅  
**Gap**: Observer table can't be soft-deleted and lacks session/user attribution. Has `is_active` boolean which partially serves the deactivation role.

```sql
-- Remediation:
ALTER TABLE observer ADD COLUMN session_id TEXT;
ALTER TABLE observer ADD COLUMN created_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE observer ADD COLUMN modified_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE observer ADD COLUMN is_deleted BOOLEAN DEFAULT false;
```

---

#### 6. `biological_property` — Missing 4 of 6 audit columns

| Missing Column    | Expected Type |
|-------------------|---------------|
| `session_id`      | `TEXT`        |
| `created_by_id`   | `UUID`        |
| `modified_by_id`  | `UUID`        |
| `is_deleted`      | `BOOLEAN`     |

**Existing audit columns**: `created_at` ✅, `modified_at` ✅  
**Gap**: Reference/lookup table lacking full audit trail.

```sql
-- Remediation:
ALTER TABLE biological_property ADD COLUMN session_id TEXT;
ALTER TABLE biological_property ADD COLUMN created_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE biological_property ADD COLUMN modified_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE biological_property ADD COLUMN is_deleted BOOLEAN DEFAULT false;
```

---

#### 7. `development_stage` — Missing 4 of 6 audit columns

| Missing Column    | Expected Type |
|-------------------|---------------|
| `session_id`      | `TEXT`        |
| `created_by_id`   | `UUID`        |
| `modified_by_id`  | `UUID`        |
| `is_deleted`      | `BOOLEAN`     |

**Existing audit columns**: `created_at` ✅, `modified_at` ✅  
**Gap**: Reference/lookup table lacking full audit trail.

```sql
-- Remediation:
ALTER TABLE development_stage ADD COLUMN session_id TEXT;
ALTER TABLE development_stage ADD COLUMN created_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE development_stage ADD COLUMN modified_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE development_stage ADD COLUMN is_deleted BOOLEAN DEFAULT false;
```

---

#### 8. `system_config` — Missing all but `modified_at`

| Missing Column    | Expected Type |
|-------------------|---------------|
| `session_id`      | `TEXT`        |
| `created_at`      | `TIMESTAMPTZ` |
| `created_by_id`   | `UUID`        |
| `modified_by_id`  | `UUID`        |
| `is_deleted`      | `BOOLEAN`     |

**Existing audit columns**: `modified_at` ✅  
**Assessment**: `system_config` is a key-value configuration table, likely not transactional in the same sense as intake/egg/bin. Drift risk is lower here.

```sql
-- Remediation (optional):
ALTER TABLE system_config ADD COLUMN session_id TEXT;
ALTER TABLE system_config ADD COLUMN created_at TIMESTAMPTZ DEFAULT now();
ALTER TABLE system_config ADD COLUMN created_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE system_config ADD COLUMN modified_by_id UUID REFERENCES observer(observer_id);
ALTER TABLE system_config ADD COLUMN is_deleted BOOLEAN DEFAULT false;
```

---

## Tables Found But Not In Key Spec List

| Table        | Notes |
|--------------|-------|
| `system_log` | Append-only event log; has `session_id`, `timestamp`, `observer_id` but no full audit columns |
| `species`    | Reference table; has `created_at`, `modified_at` but missing `session_id`, `created_by_id`, `modified_by_id`, `is_deleted` |

These tables exist in the database but were not listed in the "key tables to audit" section of the design spec. They may be intentionally omitted or represent undocumented schema expansion.

---

## Summary

| Table                 | session_id | created_at | modified_at | created_by_id | modified_by_id | is_deleted | COMPLIANT |
|-----------------------|:----------:|:----------:|:-----------:|:-------------:|:--------------:|:----------:|:---------:|
| `intake`              | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **YES** |
| `bin`                 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **YES** |
| `egg`                 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **YES** |
| `bin_observation`     | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | NO |
| `egg_observation`     | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | NO |
| `hatchling_ledger`    | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | NO |
| `session_log`         | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | NO |
| `observer`            | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | NO |
| `biological_property` | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | NO |
| `development_stage`   | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | NO |
| `system_config`       | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | NO |

### Severity Triage

| Severity | Tables Affected | Impact |
|----------|----------------|--------|
| **HIGH** | `bin_observation`, `egg_observation` | Missing `created_at` prevents accurate audit of observation creation time. These are high-volume transactional tables. |
| **HIGH** | `hatchling_ledger` | Missing user attribution columns for hatchling records. |
| **MEDIUM** | `observer` | Can't soft-delete or track who created/modified observer records. |
| **LOW** | `session_log`, `biological_property`, `development_stage`, `system_config` | These are reference/log/config tables where full audit trail is less critical but still non-compliant. |

### Recommendation

1. **Immediate**: Add `created_at` to `bin_observation` and `egg_observation` (impact: high-volume tables, fixable with backfill).
2. **Next sprint**: Add `created_by_id` and `modified_by_id` to `hatchling_ledger`.
3. **Evaluate**: Determine whether reference tables (`observer`, `biological_property`, `development_stage`, `system_config`, `session_log`) require full audit column compliance or if a reduced audit standard is acceptable for non-transactional entities.
