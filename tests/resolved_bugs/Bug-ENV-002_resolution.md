---
component: "scripts/run_e2e_tests.sh"
issue_type: "E2E Harness / Port Binding / Readiness"
resolved: true
---
# Bug-ENV-002: Playwright E2E Runner Assumed Port 8501 Without Enforcing It

**Issue**: After installing the missing Python test dependencies, the first Playwright test still failed before application assertions. Focused reproduction showed `Page.goto("http://localhost:8501")` failing with `net::ERR_CONNECTION_REFUSED`. Streamlit startup logs proved the app had auto-bound to `http://localhost:8502` instead of `8501`, while the Playwright tests and prior handoff assumptions were hardcoded to `8501`.

**Root Cause**: `/a0/usr/workdir/scripts/run_e2e_tests.sh` launched Streamlit without `--server.port 8501` and relied on a fixed `sleep 6` boot delay. When port `8501` was unavailable or Streamlit selected the next free port, the runner still launched tests against `http://localhost:8501`, causing deterministic connection failures. The fixed sleep also provided no proof of actual readiness.

**Resolution**:
1. Patched `/a0/usr/workdir/scripts/run_e2e_tests.sh` to force `streamlit run app.py --server.port 8501`.
2. Replaced the fixed sleep with an explicit readiness probe loop against `http://localhost:8501`.
3. Added shell safety flags and `trap`-based cleanup so Streamlit is terminated even when pytest exits non-zero.

**Forensic Notes**:
- This was a test harness defect, not a product logic defect.
- The symptom manifested as an apparent Playwright navigation failure in the first test.
- The failure became visible only after `pytest` and `playwright` were installed and the suite could actually execute.

**Files / Locations Referenced**:
- `/a0/usr/workdir/scripts/run_e2e_tests.sh`
- `/a0/usr/workdir/tests/e2e_playwright/test_adversarial_forensic.py`
- `/a0/usr/workdir/streamlit_focus.log`
- `/a0/usr/workdir/focused_pytest.log`

**Verification Target**:
- Re-run the focused adversarial Playwright test after the harness patch.
- Then re-run the full E2E suite to see the next genuine failure, if any.
