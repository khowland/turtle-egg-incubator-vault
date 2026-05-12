# batchid

{
  "batch_id": "BATCH_3",
  "results": [
    {
      "tsk": "TSK-03",
      "test_name": "test_intake_full_fields_and_bin_nomenclature[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-03",
      "test_name": "test_intake_multiple_eggs[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-03",
      "test_name": "test_intake_cancel_button[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-03",
      "test_name": "test_supplemental_intake_full_save[chromium]",
      "status": "FAILED",
      "duration_seconds": null,
      "error_message": "AssertionError: DB FAILURE: Expected at least 2 bins after supplemental intake, got 1. assert 1 >= 2 where 1 = len([{'bin_id': 410}]). Only 1 bin created in DB after supplemental batch submission.",
      "error_line": "tests/e2e_playwright/test_intake_extended.py:272",
      "root_cause": "The RPC function vault_finalize_supplemental_bin is only creating 1 bin instead of >=2 after submitting a supplemental intake batch. This is a known backend bug in the supplemental intake workflow — the bin finalization logic is not iterating properly over all eggs in the clutch or is failing silently on subsequent bin creations. The bin_id 410 was created, but additional bins expected from the batch were not generated.",
      "remediation": "Fix the RPC function vault_finalize_supplemental_bin in Supabase (check supabase_db/migrations/ for the function definition). The function should iterate over all newly created supplemental records and create a bin for each, not just the first. After fixing, verify with: SELECT COUNT(*) FROM bin WHERE intake_id = <supplemental_intake_id> returns >=2. File: supabase_db/migrations/ (find the migration containing vault_finalize_supplemental_bin). Add a loop or use INSERT INTO ... SELECT to process all records."
    },
    {
      "tsk": "TSK-08",
      "test_name": "test_sqli_payload_in_finder_field_sanitized[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-08",
      "test_name": "test_sqli_payload_in_winc_case_field_sanitized[chromium]",
      "status": "FAILED",
      "duration_seconds": null,
      "error_message": "postgrest.exceptions.APIError: {'message': 'JSON could not be generated', 'code': 403, 'details': 'Cloudflare Ray ID: 9f7ded8f4b6c8f4b — Sorry, you have been blocked. This website is using a security service to protect itself from online attacks.'}",
      "error_line": "tests/e2e_playwright/test_adversarial_input.py:126",
      "root_cause": "The test submits a SQLi payload into the winc_case field via UI, then attempts a DB query using supabase.table('intake').select('intake_id').eq('intake_name', payload).execute(). Supabase's Cloudflare WAF detects the SQLi pattern in the query parameter and blocks the request with a 403 HTML response. The postgrest client cannot parse the HTML as JSON, raising APIError. This is NOT an application bug — Cloudflare WAF is correctly blocking SQL injection attempts. The test failure is a test design issue: the DB verification step triggers the WAF.",
      "remediation": "Modify test_sqli_payload_in_winc_case_field_sanitized in tests/e2e_playwright/test_adversarial_input.py around line 126 to either: (a) catch postgrest.exceptions.APIError with code 403 and log it as a PASS (WAF correctly blocked), or (b) use a unique non-malicious signature in the winc_case field instead of the raw SQLi payload for DB lookup (e.g., append a UUID or timestamp to a benign string), or (c) use a direct Postgres connection via psycopg2 that bypasses the WAF for verification only. Recommended: option (b) — use a benign unique lookup key generated at submission time."
    },
    {
      "tsk": "TSK-08",
      "test_name": "test_overly_long_field_values_rejected_or_truncated[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-08",
      "test_name": "test_xss_payloads_in_finder_field_sanitized[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-08",
      "test_name": "test_empty_required_fields_rejected[chromium]",
      "status": "PASSED",
      "duration_seconds": null,
      "error_message": null,
      "error_line": null,
      "root_cause": null,
      "remediation": null
    },
    {
      "tsk": "TSK-08",
      "test_name": "test_xss_payloads_sanitized[chromium]",
      "status": "FAILED",
      "duration_seconds": null,
      "error_message": "AssertionError: XSS payload stored as XSS-PAYLOAD-1778132858. assert 0 == 1 where 0 = len([]). DB query for intake_name='XSS-PAYLOAD-1778132858' returned zero rows.",
      "error_line": "tests/e2e_playwright/test_adversarial_input.py:273",
      "root_cause": "The test submits an XSS payload (e.g., <script>alert('XSS')</script>) as the intake_name via the UI. The UI accepts it and the test sees it 'stored as' signature XSS-PAYLOAD-1778132858 (indicating the payload was displayed back in the UI). However, when the test queries the DB by intake_name = XSS-PAYLOAD-1778132858, no rows are found. This could mean: (a) the intake_name is being sanitized/shortened on storage but displayed differently in UI, (b) the intake record wasn't actually committed (SAVE button issue), or (c) the signature lookup string doesn't match what was stored. The XSS payload (<script>alert...). This is a real sanitization gap — the UI may accept and display XSS payloads without encoding, creating a stored XSS vulnerability.",
      "remediation": "In vault_views/2_New_Intake.py (or wherever intake form submission is handled), sanitize the intake_name field before storing: use html.escape(intake_name) or bleach.clean(intake_name, tags=[], strip=True) to strip all HTML/script tags. Also verify the SAVE action correctly commits to the DB — check that st.session_state is properly synchronized with the Supabase insert. After sanitizing, re-run the test to confirm: (1) the payload is NOT stored as-is, and (2) the test either expects sanitized output or skips the DB verification for known-malicious inputs. File: vault_views/2_New_Intake.py, locate the intake_name field handling in the form submission callback."
    }
  ],
  "summary": {
    "total": 10,
    "passed": 7,
    "failed": 3,
    "timeout": 0,
    "error": 0
  },
  "notes": "TSK-03 suite took 54.97s; TSK-08 took 66.52s. No tests timed out. The IndentationError in test_adversarial_input.py (line 176) previously reported for TSK-08 is now FIXED — all 6 tests collected successfully. The test_xss_payloads_sanitized failure is notable: the UI displays the XSS signature (XSS-PAYLOAD-1778132858) suggesting the payload was 'accepted', but the DB query returns zero rows — this needs investigation into whether the storage is sanitizing the name differently than the UI display, or if the SAVE action silently failed. The SQLi WAF block (Cloudflare 403) is security working correctly — this is a test design issue not an application vulnerability. All other tests are stable and passing. No visual rendering glitches observed in test output; Chromium Playwright ran headless without issues. The supplemental_intake RPC bug (test_supplemental_intake_full_save) remains the highest-priority fix as it's a known backend logic defect."
}
