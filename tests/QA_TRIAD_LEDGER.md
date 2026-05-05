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
| TSK-02 | `TEST_MATRIX_REPORTS.md` | `[TODO]` | Writer | 0 | Pending creation based on Master Plan Phase 1. |
| TSK-03 | `test_intake_extended.py` | `[NEEDS_VALIDATION]` | Validator | 1 | Runner fix: added _fill_intake_step1_fields helper. 3 of 4 tests failed due to incomplete form fills. |
| TSK-04 | `test_observation_workflows.py` | `[NEEDS_VALIDATION]` | Validator | 1 | Runner fix: added required Intake field fills to _setup_intake_and_unlock_grid. All 7 tests failed due to missing Species/Condition/etc. fields. |
| TSK-05 | `test_adversarial_intake.py` | `[TODO]` | Writer | 0 | Awaiting Writer to draft hostile payload tests. |
| TSK-06 | `test_adversarial_observations.py` | `[TODO]` | Writer | 0 | Awaiting Writer to draft hostile payload tests. |
| TSK-07 | `test_phase5_scalability_loop.py` | `[TODO]` | Writer | 0 | Awaiting Writer to draft the 50x execution loop. |

---

## 🛑 Strike Out (Needs Work) Log

*Files that hit Strike 3 are moved here. A human architect must clear them.*

| Task ID | Component/File | Post-Mortem File Link | Reason for Lock |
| :--- | :--- | :--- | :--- |
| *None* | *None* | *None* | *System Clean* |
