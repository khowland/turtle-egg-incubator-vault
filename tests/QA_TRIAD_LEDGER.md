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
| TSK-03 | `test_intake_extended.py` | `[DEPRECATED_STREAMLIT]` | — | — | DEPRECATED: Streamlit is deprecated. React is the target platform. Test preserved for reference; hardened with retry loops. |
| TSK-04 | `test_observation_workflows.py` | `[DEPRECATED_STREAMLIT]` | — | — | DEPRECATED: Streamlit is deprecated. Bridging bug fix applied (conftest.py line 110) for reference. |
| TSK-05 | `test_adversarial_intake.py` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: 7/7 adversarial tests passed. All DB Pincer assertions pass. |
| TSK-06 | `test_adversarial_observations.py` | `[DEPRECATED_STREAMLIT]` | — | — | DEPRECATED: Streamlit is deprecated. React is the target platform. |
| TSK-07 | `test_phase5_scalability_loop.py` | `[DEPRECATED_STREAMLIT]` | — | — | DEPRECATED: Streamlit is deprecated. React is the target platform. |
| TSK-08 | `test_adversarial_input.py` | `[DEPRECATED_STREAMLIT]` | — | — | DEPRECATED: Streamlit is deprecated. Test hardening applied (to_be_attached, retry loops). |
| **React-TSK-01** | `test_react_sovereign_ping.py` | `[GREEN_COMPLETED]` | Runner | 0 | PASSED: 1/1 test. React app sovereignty confirmed at http://localhost:5173. Version v9.7.0 from system_config verified. Sidebar, Dashboard heading, KPI metrics all visible. |

---

## 🛑 Strike Out (Needs Work) Log

*Files that hit Strike 3 are moved here. A human architect must clear them.*

| Task ID | Component/File | Post-Mortem File Link | Reason for Lock |
| :--- | :--- | :--- | :--- |
| *None* | *None* | *None* | *System Clean* |

---

## 🚫 Deprecated — Streamlit Bridging Bug

**Root Cause**: `active_case_id` is stored in `st.session_state` but NOT bridged to Playwright's session state after `switch_page` navigation. This leaves `workbench_bins` empty → multi-select options & selectbox dropdowns never populate → tests hang/timeout.

**Status:** All Streamlit tests deprecated as of 2026-05-22 (Sprint 6). React is now the sole target platform.

---

## ✅ Sprint 6 Completion Summary (2026-05-22)

| Commit | Description | Task(s) |
|--------|-------------|---------|
| `2d18a46` | `security(keys): rotate SERVICE_ROLE to verified anon key` | **C1** — Key rotation + RLS deployed |
| `6e08962` | `feat: Sprint 6 core — atomic observations, real observer context, live dashboard` | **H1, M5, M7, M8** — Atomic RPC, observer from DB, live dashboard data |
| `b5be8cb` | `fix(react): resolve hydration crash — observer_id type mismatch` | **React** — Sidebar crash fix (bigint→string) |
| `5f0f236` | `fix(observations): wire up saving state and saveError banner` | **TypeScript** — Build fix for unused variables |
| `4609cbc` | `test: harden Streamlit E2E tests with retry loops and attached assertions` | **Test hardening** — Retry loops, assertion fixes |

**All Sprint 6 deliverables complete. React app sovereignty verified. Production build ready (dist/). Streamlit platform fully deprecated.**
