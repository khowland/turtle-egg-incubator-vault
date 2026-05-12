# 🤹 The QA Triad Ledger (State Machine)

**Classification:** MASTER CONTROL DOCUMENT
**Purpose:** Orchestrates the 3-way QA Triad (Writer, Validator, Runner). This is the single source of truth for all autonomous QA operations.

## 🚦 Ledger Rules (Read Before Modifying)

1. **Strict Handoffs:** An agent may ONLY process a file if the `Status` matches their assigned role (Writer = `[TODO]`, Validator = `[NEEDS_VALIDATION]`, Runner = `[READY_TO_RUN]`).
2. **No Backwards Drift:** A file moving backward (e.g., Runner sends back to Writer) increments the Strike Count.
3. **Strike 3 Protocol:** If `Strike Count` hits 3, status becomes `[HARD_LOCK]`. The file is removed from active rotation and a `NEEDS_WORK_{filename}.md` report is generated.

---

## 📋 Active Task Ledger

| Task ID | Component/File | Status | Current Owner | Strike Count | Last Action / Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TSK-01 | `TEST_MATRIX_SETTINGS.md` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: documentation artifact. 18 test cases verified. |
| TSK-02 | `TEST_MATRIX_REPORTS.md` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: documentation artifact. 14 test cases verified. |
| TSK-03 | `test_intake_extended.py` | `[READY_TO_RUN]` | Runner | 1 | 3/5 passed. TC-SUP-01: RPC vault_finalize_supplemental_bin not creating bin (expected >=2, got 1). test_50x_observation_loop: Stage selectbox timeout (bridging bug). Supplemental test (TC-SUP-01) expected 2 bins, got 1 — vault_finalize_supplemental_bin RPC not creating bin. 500ms+nav pattern applied. |
| TSK-04 | `test_observation_workflows.py` | `[BLOCKED_BRIDGING]` | Runner | 2 | BLOCKED: active_case_id not bridged to Playwright session state after switch_page. All 7 tests hang on multi-select dropdown. Fix: bridge session state before selectbox interaction. |
| TSK-05 | `test_adversarial_intake.py` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: 7/7 adversarial tests passed. All DB Pincer assertions pass. |
| TSK-06 | `test_adversarial_observations.py` | `[BLOCKED_BRIDGING]` | Runner | 0 | BLOCKED: Same active_case_id bridging bug as TSK-04/TSK-07. All 5 tests fail on stSelectboxVirtualDropdown locator timeout (S2, S4, S6, S7 options never appear). |
| TSK-07 | `test_phase5_scalability_loop.py` | `[BLOCKED_BRIDGING]` | Runner | 1 | BLOCKED: Same active_case_id bridging bug. test_50x_observation_loop: Stage stSelectbox not visible after scalability loop (TimeoutError). |
| TSK-08 | `test_adversarial_input.py` | `[READY_TO_RUN]` | Runner | 0 | IndentationError at line 176 FIXED. 6 tests collected. Awaiting v2 Triad rerun. |

---

## 🛑 Strike Out (Needs Work) Log

*Files that hit Strike 3 are moved here. A human architect must clear them.*

| Task ID | Component/File | Post-Mortem File Link | Reason for Lock |
| :--- | :--- | :--- | :--- |
| *None* | *None* | *None* | *System Clean* |

## 🚫 Bridging Bug Blocked Tests

**Root Cause**: `active_case_id` is stored in `st.session_state` but NOT bridged to Playwright's session state after `switch_page` navigation. This leaves `workbench_bins` empty → multi-select options & selectbox dropdowns never populate → tests hang/timeout.

**Affected TSKs**: TSK-04 (7 tests), TSK-06 (5 tests), TSK-07 (1 test) = **13 tests blocked total**

**Remediation**: Bridge `active_case_id` into Playwright session state after `switch_page` calls, or use direct URL navigation with query parameters. Fix must be applied in `conftest.py` or a shared helper.

- **TSK-04 RESOLUTION**: Replace line 109 in conftest.py with Vision-First coordinate click at **(640, 457)**.

