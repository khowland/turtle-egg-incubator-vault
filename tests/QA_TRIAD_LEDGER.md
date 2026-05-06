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
| TSK-03 | `test_intake_extended.py` | `[TODO]` | Writer | 0 | Reopened: st.data_editor eliminated per CR-P1-01. Rewrite tests for st.number_input selector. Previous Strike count reset. |
| TSK-04 | `test_observation_workflows.py` | `[READY_TO_RUN]` | Runner | 2 | Validator PASS: dvn-cell fix applied. Bug-E2E-002 resolved (TSK-05 confirmed 7/7 pass). Awaiting Runner execution. |
| TSK-05 | `test_adversarial_intake.py` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: 7/7 adversarial tests passed. Bug-E2E-002 dvn-cell fix validated. All DB Pincer assertions pass. |
| TSK-06 | `test_adversarial_observations.py` | `[TODO]` | Writer | 0 | Reopened: Stage jump validation enforced per CR-P2-01. Write adversarial tests validating enforcement + surgical_resurrection flag. |
| TSK-07 | `test_phase5_scalability_loop.py` | `[READY_TO_RUN]` | Runner | 0 | Validator PASS: DB Pincers, e2e_selectors, comment standards all verified. Greenlet runtime error is environmental, not code defect. |

---

## 🛑 Strike Out (Needs Work) Log

*Files that hit Strike 3 are moved here. A human architect must clear them.*

| Task ID | Component/File | Post-Mortem File Link | Reason for Lock |
| :--- | :--- | :--- | :--- |
| *None* | *None* | *None* | *System Clean* |
| TSK-03 | `test_intake_extended.py` | tests/resolved_bugs/NEEDS_WORK_TSK-03.md | STRIKE 3: data_editor/dvn-cell issues. **CLEARED 2026-05-05** — st.data_editor eliminated by CR-P1-01. Task reopened to [TODO]. |
