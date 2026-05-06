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
| TSK-03 | `test_intake_extended.py` | `[READY_TO_RUN]` | Runner | 0 | 3/4 passed (primary tests green). Supplemental test (TC-SUP-01) expected 2 bins, got 1 — vault_finalize_supplemental_bin RPC not creating bin. 500ms+nav pattern applied. |
| TSK-04 | `test_observation_workflows.py` | `[READY_TO_RUN]` | Runner | 2 | Validator PASS. Cat-A helper cascade + Cat-D navigation timing fixes applied. Awaiting Runner execution. |
| TSK-05 | `test_adversarial_intake.py` | `[GREEN_COMPLETED]` | Runner | 0 | Completed: 7/7 adversarial tests passed. All DB Pincer assertions pass. |
| TSK-06 | `test_adversarial_observations.py` | `[NEEDS_WORK]` | Writer | 0 | Validator found: missing surgical_resurrection bypass test, no-op assertion in TC-ADV-OBS-04, missing DB pincer. |
| TSK-07 | `test_phase5_scalability_loop.py` | `[READY_TO_RUN]` | Runner | 1 | Strike 1: multiselect dropdown timeout (bin_code not found). Root cause: 409 Conflict race condition (FIXED by Kevin). Awaiting re-run. |
| TSK-08 | `test_adversarial_input.py` | `[NEEDS_WORK]` | Writer | 0 | Validator found: XSS payloads unused, no-op assertion in TC-ADV-INP-03, no SQLi sanitization verification. |

---

## 🛑 Strike Out (Needs Work) Log

*Files that hit Strike 3 are moved here. A human architect must clear them.*

| Task ID | Component/File | Post-Mortem File Link | Reason for Lock |
| :--- | :--- | :--- | :--- |
| *None* | *None* | *None* | *System Clean* |
