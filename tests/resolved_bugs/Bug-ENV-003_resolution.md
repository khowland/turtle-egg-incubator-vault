---
component: "scripts/run_e2e_tests.sh"
issue_type: "E2E Harness / Stale Port Ownership"
resolved: true
---
# Bug-ENV-003: E2E Runner Failed When Port 8501 Was Already Occupied

**Issue**: Even after forcing Streamlit to use port `8501`, repeated or sequential E2E runs still failed intermittently with `ERR_CONNECTION_REFUSED`. Investigation showed the runner could start while `8501` was already occupied by a stale Streamlit process from a prior interrupted run. In that state, the new Streamlit process logged `Port 8501 is not available`, and Playwright subsequently failed to connect to the expected app instance.

**Root Cause**: The E2E harness did not proactively clear stale ownership of port `8501` before launching a new Streamlit process. Prior hangs and interrupted test runs left orphaned processes behind, causing later launches to fail silently into a port-conflict state.

**Resolution**:
1. Updated `/a0/usr/workdir/scripts/run_e2e_tests.sh` to kill any process bound to `8501` before startup.
2. Preserved forced binding to `--server.port 8501`.
3. Extended cleanup to also clear the port on exit.

**Verification Target**:
- Re-run the full Playwright E2E suite after the stale-port cleanup patch.
