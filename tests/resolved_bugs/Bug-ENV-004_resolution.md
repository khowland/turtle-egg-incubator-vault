---
component: "E2E Playwright Harness"
issue_type: "Harness Architecture / Fixed Port Coupling"
resolved: true
---
# Bug-ENV-004: Fixed-Port Playwright Harness Caused Non-Deterministic E2E Failures

**Issue**: The Playwright E2E suite was tightly coupled to `http://localhost:8501` across multiple test files and shell runners. Repeated runs produced non-deterministic `ERR_CONNECTION_REFUSED` failures due to stale port ownership, race conditions, and drift between shell scripts.

**Root Cause**: The suite relied on a fixed port, duplicated lifecycle logic, and hardcoded URLs inside tests rather than a single launcher-controlled base URL.

**Resolution**:
1. Added a canonical Python launcher at `/a0/usr/workdir/scripts/e2e_launcher.py`.
2. The launcher now allocates a free local port dynamically, starts Streamlit in its own process group, waits for HTTP readiness, exports `E2E_BASE_URL`, runs pytest, and tears Streamlit down deterministically.
3. Added `/a0/usr/workdir/tests/e2e_playwright/conftest.py` to centralize `E2E_BASE_URL` and shared login behavior.
4. Refactored Playwright tests to use the shared login fixture instead of hardcoded `http://localhost:8501` literals.
5. Reduced shell wrappers to thin shims that call the Python launcher.
