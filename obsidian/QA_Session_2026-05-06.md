---
title: QA Session 2026-05-06
date: 2026-05-06
tags:
  - qa-triad
  - bug-log
  - winc-incubator
status: in-progress
---

# QA Triad Session — 2026-05-06

## Bugs Discovered

> [!bug] BUG-E2E-003: vault_finalize_intake 409 Conflict Race Condition
> **Severity:** Critical  
> **Status:** Fixed by Kevin  
> **Root Cause:** `v_intake_id` generated with second-level precision (`HH24MS`), causing duplicate PK on concurrent inserts.  
> **Fix:** Changed to `HH24MISSMS` (millisecond precision).  
> **Impact:** Blocked TSK-03, TSK-07 (intakes not created).

> [!bug] BUG-E2E-004: vault_finalize_intake Missing observer_name
> **Severity:** Critical  
> **Status:** Fixed by Kevin  
> **Root Cause:** RPC INSERT into bin_observation omitted NOT NULL column `observer_name`.  
> **Fix:** Migration `v9_2_1_FIX_FINALIZE_INTAKE_OBSERVER_NAME.sql` — extracts display_name from observer table.  
> **Impact:** Blocked all intake saves (HTTP 400 Bad Request).

> [!bug] BUG-CONFTEST-001: Conftest.py SyntaxError
> **Severity:** Blocker  
> **Status:** Fixed  
> **Root Cause:** Malformed try/except indentation in soft-delete fixture (lines 59-74).  
> **Fix:** Corrected indentation of id_map dict and related statements.

> [!bug] BUG-CONFTEST-002: Conftest.py UUID .neq Crash
> **Severity:** Medium  
> **Status:** Fixed  
> **Root Cause:** Soft-delete fixture used `.neq(id_col, 0)` which fails on UUID PK (hatchling_ledger).  
> **Fix:** Moved hatchling_ledger to skip_tables.

> [!failure] TSK-03: Supplemental Intake SAVE Not Creating Bin
> **Status:** Unresolved  
> **Symptom:** Expected 2 bins after supplemental intake, got 1.  
> **Diagnosis:** vault_finalize_supplemental_bin RPC may not be called or is failing silently. No RPC log entries found.  
> **Test File:** [[test_intake_extended.py]]

> [!failure] TSK-07: Multi-Select Dropdown Timeout (Strike 1)
> **Status:** Awaiting re-run after 409 fix  
> **Symptom:** Locator.click timeout on multi-select dropdown finding bin_code.  
> **Likely Cause:** Race condition 409 Conflict prevented intake creation, so no bins available.  
> **Test File:** [[test_phase5_scalability_loop.py]]

## Test Fixes Applied

> [!success] TSK-03 Navigation Pattern Fix
> All 3 SAVE points now use: `page.wait_for_timeout(500)` → `NAV_OBSERVATIONS` click → `expect(heading).to_be_visible(timeout=15000)`. Resolved TimeoutErrors.

> [!success] TSK-03 bin_id Type Fix
> Nomenclature assertion now checks `bin_code` (text) instead of `bin_id` (BIGINT).

> [!success] TSK-03 Import Fix
> Added `NAV_OBSERVATIONS` to e2e_selectors import.

## Validator Results

> [!warning] TSK-06: [[test_adversarial_observations.py]] — NEEDS_WORK
> - Missing surgical_resurrection bypass test
> - TC-ADV-OBS-04 no-op assertion
> - Missing DB pincer in TC-ADV-OBS-02

> [!warning] TSK-08: [[test_adversarial_input.py]] — NEEDS_WORK
> - XSS payloads defined but never executed
> - No SQLi sanitization DB verification
> - TC-ADV-INP-03 no-op assertion

---

## Related
- [[QA_TRIAD_LEDGER]]
- [[BREADCRUMB]]
- [[00_CENTRAL_HUB]]
