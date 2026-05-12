---
date: 2026-05-07 00:50
tags: [batch-3, tsk-03, tsk-08, test-results]
status: completed
---

# Batch 3 Results — TSK-03 + TSK-08

> [!info] Tactic 1 — Claude (vision) test runner
> Fresh context, reset=true. 10 tests total across 2 files.

## Results: 7/10 Passed (70%)

| # | TSK | Test | Status | Duration | Failure Reason |
|---|-----|------|--------|----------|---------------|
| 1 | TSK-03 | test_intake_full_fields_and_bin_nomenclature | ✅ PASSED | ~11s | — |
| 2 | TSK-03 | test_intake_multiple_eggs | ✅ PASSED | ~11s | — |
| 3 | TSK-03 | test_intake_cancel_button | ✅ PASSED | ~11s | — |
| 4 | TSK-03 | test_supplemental_intake_full_save | ❌ FAILED | ~11s | RPC vault_finalize_supplemental_bin creates only 1 bin |
| 5 | TSK-08 | test_sqli_payload_in_finder_field_sanitized | ✅ PASSED | ~11s | — |
| 6 | TSK-08 | test_sqli_payload_in_winc_case_field_sanitized | ❌ FAILED | ~11s | Cloudflare WAF 403 (security working — test design issue) |
| 7 | TSK-08 | test_overly_long_field_values_rejected_or_truncated | ✅ PASSED | ~11s | — |
| 8 | TSK-08 | test_xss_payloads_in_finder_field_sanitized | ✅ PASSED | ~11s | — |
| 9 | TSK-08 | test_empty_required_fields_rejected | ✅ PASSED | ~11s | — |
| 10 | TSK-08 | test_xss_payloads_sanitized | ❌ FAILED | ~11s | XSS payload stored as intake_name — no sanitization |

## Failures

### TSK-03: test_supplemental_intake_full_save
- **Root cause**: RPC vault_finalize_supplemental_bin creates only 1 bin (expected >=2)
- **Remediation**: Fix Supabase RPC function to iterate over all supplemental records
- **TSDQ**: TSDQ-002

### TSK-08: test_sqli_payload_in_winc_case_field_sanitized
- **Root cause**: Supabase Cloudflare WAF blocks SQLi query — security working
- **Remediation**: Update test to expect 403 or use benign lookup key
- **Not a real vulnerability**

### TSK-08: test_xss_payloads_sanitized
- **Root cause**: `<script>alert('XSS')</script>` accepted and displayed in intake_name
- **Remediation**: Add `html.escape()` in vault_views/2_New_Intake.py
- **Real stored XSS vulnerability**

## Next Actions
- Fix TSK-08 XSS (2_New_Intake.py)
- Fix TSK-08 SQLi test (expect WAF 403)
- Investigate RPC function for TSDQ-002
- Validate TSDQ-001 bridging fix with TSK-07 smoke test
