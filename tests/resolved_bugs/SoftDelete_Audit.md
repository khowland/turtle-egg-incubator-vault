# 🛡️ Soft-Delete Filter Audit Report

**Date:** 2026-05-03  
**Version:** v9.1.0  
**Mandate:** All queries against tables with `is_deleted` column MUST filter `is_deleted=false` to prevent soft-deleted rows from appearing in the UI.

---

## 📊 Summary

| Metric | Value |
|---|---|
| Files audited | 8 (vault_views/*.py + utils/*.py) |
| Tables with `is_deleted` | 6 (egg, bin, intake, egg_observation, bin_observation, hatchling_ledger) |
| Queries checked | All `.table(...)`.select() calls |
| **Violations found** | **14** |
| **Files affected** | **6** |

---

## 🔴 Violations: SELECT Queries Missing `is_deleted` Filter

### File: `vault_views/1_Dashboard.py`

| Line | Table | Issue | Risk |
|---|---|---|---|
| 129 | `egg` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Dashboard egg stats could include deleted eggs |

### File: `vault_views/2_New_Intake.py`

| Line | Table | Issue | Risk |
|---|---|---|---|
| 94 | `intake` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Intake listing could show deleted cases |
| 109 | `bin` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Supplemental bin edit could show deleted bins |

### File: `vault_views/3_Observations.py`

| Line | Table | Issue | Risk |
|---|---|---|---|
| 49 | `bin` | SELECT without `.eq("is_deleted", False)` | 🔴 HIGH — Workbench multiselect could show deleted bins |
| 85 | `egg_observation` | SELECT without `.eq("is_deleted", False)` | 🔴 HIGH — Observed-this-session tracking could count voided observations |
| 158 | `bin_observation` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Weight gate last reading could use voided data |
| 289 | `egg` | SELECT without `.eq("is_deleted", False)` | 🔴 HIGH — Surgical egg search could show deleted eggs |
| 665 | `egg` | SELECT without `.eq("is_deleted", False)` | 🔴 HIGH — S6 batch transition context query |
| 667 | `bin` | SELECT without `.eq("is_deleted", False)` | 🔴 HIGH — S6 batch transition context query |
| 670 | `hatchling_ledger` | SELECT without `.eq("is_deleted", False)` | 🔴 HIGH — S6 ledger upsert collision check |

### File: `vault_views/5_Settings.py`

| Line | Table | Issue | Risk |
|---|---|---|---|
| 436 | `intake` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Admin restore health check |

### File: `vault_views/6_Reports.py`

| Line | Table | Issue | Risk |
|---|---|---|---|
| 336 | `hatchling_ledger` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Reports could include voided hatchling records |

### File: `utils/bootstrap.py`

| Line | Table | Issue | Risk |
|---|---|---|---|
| 323 | `bin_observation` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Last bin weight cache could use voided data |
| 338 | `bin` | SELECT without `.eq("is_deleted", False)` | 🟡 MEDIUM — Fallback weight from bin metadata |

---

## 📋 Affected Tables Summary

| Table | Violations | Highest Risk |
|---|---|---|
| `egg` | 3 | 🔴 HIGH |
| `bin` | 4 | 🔴 HIGH |
| `intake` | 2 | 🟡 MEDIUM |
| `egg_observation` | 1 | 🔴 HIGH |
| `bin_observation` | 2 | 🟡 MEDIUM |
| `hatchling_ledger` | 2 | 🔴 HIGH |

---

## 🛠️ Remediation Plan

### Phase 1: Critical Fixes (Observations Page)

Fix all 7 violations in `vault_views/3_Observations.py`:

```python
# Line 49 — bin query for workbench
.eq("is_deleted", False)

# Line 85 — egg_observation query for observed-this-session
.eq("is_deleted", False)

# Line 158 — bin_observation query for last weight
.eq("is_deleted", False)

# Line 289 — egg query for surgical search
.eq("is_deleted", False)

# Lines 665, 667, 670 — S6 batch transition context queries
.eq("is_deleted", False)  # for egg, bin, hatchling_ledger
```

### Phase 2: Dashboard & Intake

Fix 3 violations in `1_Dashboard.py` and `2_New_Intake.py`.

### Phase 3: Settings, Reports, Utils

Fix 4 violations in `5_Settings.py`, `6_Reports.py`, `utils/bootstrap.py`.

---

## ⚠️ Special Considerations

1. **Surgical Correction Mode:** In `3_Observations.py` line 289 (egg search for surgery), the query MAY need to include deleted eggs intentionally (to resurrect voided data). This needs manual review.

2. **Voided Observations Display:** Lines 422-454 in `3_Observations.py` intentionally SELECT voided (is_deleted=true) observations for display in the Resurrection Vault section. These are CORRECT — they display voided records for potential restoration.

3. **Admin Restore:** `5_Settings.py` line 436 queries intake without is_deleted filter during admin restore. May need to include deleted intakes for restoration.

---

## 📝 Audit Methodology

- Python regex scan of all `.table("tablename").select(...)` calls
- Checked context (10 lines after) for `is_deleted` string
- Manual review of edge cases (surgical mode, restore flows)
- INSERT operations excluded (they don't query existing rows)
- UPDATE operations excluded (they set specific IDs, not filtered lists)

---

**Next Step:** Apply Phase 1 fixes to `3_Observations.py` and re-run E2E tests to validate.