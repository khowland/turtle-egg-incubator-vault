---
component: "Test Execution Environment / Playwright E2E Runner"
issue_type: "Environment / Dependency Blocker"
resolved: true
---
# Bug-ENV-001: E2E Test Runner Blocked by Missing `pytest` and `playwright`

**Issue**: Resuming the authorized Playwright E2E verification failed before any application assertions executed. Running `/a0/usr/workdir/scripts/run_e2e_tests.sh` produced `/opt/venv/bin/python3: No module named pytest`. Follow-up inspection confirmed the active interpreter at `/opt/venv/bin/python3` lacked both `pytest` and `playwright`, even though `/a0/usr/workdir/requirements.txt` declares `pytest>=9.0.0` and `pytest-playwright>=0.5.0`.

**Root Cause**: The repository's active Linux Python environment was not provisioned with the project's testing dependencies. The existing `.venv` directory is Windows-style (`.venv/Scripts/...`) and was not usable as the runtime for this Kali/Linux container. As a result, the bash runner's direct `python3 -m pytest` invocation could not execute.

**Resolution**:
1. Installed project dependencies into the active interpreter using:
   - `python3 -m pip install -r /a0/usr/workdir/requirements.txt`
2. Installed the Playwright Chromium browser required by `pytest-playwright` using:
   - `python3 -m playwright install chromium`
3. Re-ran the authorized E2E suite via:
   - `/a0/usr/workdir/scripts/run_e2e_tests.sh`

**Forensic Notes**:
- This blocker was environmental, not an application logic failure.
- The remediation preserves the intended runner behavior rather than changing test invocation semantics.
- Subsequent failures after this point, if any, should be treated as genuine test or application defects per the QA methodology.

**Files / Locations Referenced**:
- `/a0/usr/workdir/scripts/run_e2e_tests.sh`
- `/a0/usr/workdir/requirements.txt`
- `/a0/usr/workdir/tests/resolved_bugs/QA_METHODOLOGY.md`
- `/a0/usr/workdir/tests/resolved_bugs/00_CENTRAL_HUB.md`

**Verification**:
- Verified dependency presence in the active environment after installation.
- Re-executed the E2E runner immediately after provisioning to move from environment validation into real suite execution.
