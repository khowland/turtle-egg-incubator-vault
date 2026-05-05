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
| TSK-01 | `TEST_MATRIX_SETTINGS.md` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: documentation artifact, no code execution. 18 test cases ready. |
| TSK-02 | `TEST_MATRIX_REPORTS.md` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: documentation artifact, no code execution. 14 test cases verified. |
| TSK-03 | `test_intake_extended.py` | `[NEEDS_VALIDATION]` | Validator | 2 | Runner Strike 2: data_editor locator stale per Bug-E2E-002; applied get_by_role textbox fixes + Streamlit rerender waits per EXTRAS solution. |
| TSK-04 | `test_observation_workflows.py` | `[NEEDS_VALIDATION]` | Validator | 2 | Runner Strike 2: same root cause as TSK-03 (stale data_editor locator, strict mode violations in _setup_intake_and_unlock_grid). Applied get_by_role textbox fixes + Streamlit waits. |
| TSK-05 | `test_adversarial_intake.py` | `[TODO]` | Writer | 0 | Awaiting Writer to draft hostile payload tests. |
| TSK-06 | `test_adversarial_observations.py` | `[TODO]` | Writer | 0 | Awaiting Writer to draft hostile payload tests. |
| TSK-07 | `test_phase5_scalability_loop.py` | `[TODO]` | Writer | 0 | Awaiting Writer to draft the 50x execution loop. |

---

## 🛑 Strike Out (Needs Work) Log

*Files that hit Strike 3 are moved here. A human architect must clear them.*

| Task ID | Component/File | Post-Mortem File Link | Reason for Lock |
| :--- | :--- | :--- | :--- |
| *None* | *None* | *None* | *System Clean* |
