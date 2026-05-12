---
date: 2026-05-07 00:15
tags: [tsk-08, test-results, adversarial-input]
status: completed
---

# TSK-08 Test Results — test_adversarial_input.py

> [!info] v2 Triad — Tactic 1 execution
> Ran after IndentationError at line 176 was fixed.

## Results: 4/6 Passed

| Test | Status | Duration | Failure Reason |
|------|--------|----------|---------------|
| test_sqli_payload_in_finder_field_sanitized | ✅ PASSED | ~15s | — |
| test_sqli_payload_in_winc_case_field_sanitized | ❌ FAILED | ~15s | Cloudflare 403 — SQLi payload triggered WAF block. This is expected security behavior, NOT a test failure. |
| test_overly_long_field_values_rejected_or_truncated | ✅ PASSED | ~15s | — |
| test_xss_payloads_in_finder_field_sanitized | ✅ PASSED | ~15s | — |
| test_empty_required_fields_rejected | ✅ PASSED | 12.88s | — |
| test_xss_payloads_sanitized | ❌ FAILED | ~15s | XSS payload `<script>alert('XSS')</script>` was stored as intake name. Assertion expected len=0 (sanitized), got len=1 (stored). The UI accepts and stores XSS in intake_name. |

## Analysis

### SQLi WAF Block (not real failure)
- The SQLi payload `'; DROP TABLE intake; --` sent to Supabase triggered Cloudflare WAF (403)
- This means Cloudflare security is WORKING - SQLi is blocked at the network edge
- **Recommendation**: Update test to expect 403 or skip this test (WAF handles it)

### XSS Payload Stored (real bug)
- `<script>alert('XSS')</script>` was accepted as intake_name and stored in DB
- This means the app does NOT sanitize/escape HTML in intake names
- **Severity**: Medium — XSS in intake names could execute if rendered unsafely
- **Fix**: Sanitize HTML in intake_name field before storage, or escape on render

## Next Actions
- SQLi test: Update assertion to expect WAF block or remove
- XSS test: Flag for developer fix (sanitize intake_name)
- Move both to TSDQ for retest after fixes
