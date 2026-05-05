# 🚀 Sprint Directive & Disaster Recovery Protocol
**Date:** 2026-05-04 22:30:00
**Component:** QA Triad Orchestration
**Status:** ACTIVE

## 🛡️ Disaster Recovery (DR) Protocol
To ensure we never start over from scratch in the event of an M6800 crash, API timeout, or agent loop, the following DR mechanisms are active:

1. **The Ledger Checkpoint (Git State):**
   Agent Zero is instructed to perform an atomic `git commit` of the `QA_TRIAD_LEDGER.md` every time a task status changes. If the system crashes, the Ledger on disk (and in git history) will perfectly reflect the last known state.
2. **The "Hard Resume":**
   In the event of a crash, **DO NOT RESTART THE SPRINT.** Simply pass the prompt to Agent Zero again. Agent Zero is hard-coded to read the Ledger first and will seamlessly pick up the exact ball that was dropped based on its `Status`.
3. **The Nuclear Reset (VHDX):**
   If the agents somehow corrupt the database permanently during testing, our `C:\DockerSafe\GOLD_BACKUP_26GB_POST_RECOVERY.vhdx` is standing by. A simple copy-paste over the live Docker file resets the entire application to "Peak Form" in 60 seconds.

---

## 📋 FINAL LAUNCH PROMPT FOR AGENT ZERO
*Pass the following prompt to A0 to initiate the automated QA execution:*

***

**ROLE:** QA Orchestrator (Agent Zero)
**MISSION:** Manage the QA Triad Workflow (Writer → Validator → Runner) without hallucination, drift, context bloat, or endless loops.

**1. THE SUPREME LAW (REQUIREMENTS OVERRIDE):**
You must locate and strictly adhere to `Requirements.md` and `implied_system_objective.md`. You must follow Enterprise QA Standards, existing project coding style, and comment standards. 
*Constraint:* **Targeted Retrieval Only.** You are strictly prohibited from bulk-reading the repository. Use `grep_search` to find relevant components.

**2. THE DISCREPANCY STOP RULE (EMERGENCY BRAKE):**
If at ANY point you discover a discrepancy between your current testing task and the rules defined in `Requirements.md` or `implied_system_objective.md`:
*   **STOP IMMEDIATELY.** Do not attempt to code a workaround.
*   Change the task status in the Ledger to `[HARD_LOCK_DISCREPANCY]`.
*   Generate a discrete file named `tests/resolved_bugs/DISCREPANCY_{TaskID}.md`. Detail exactly how the application state conflicts with the written requirements.
*   Move immediately to the next task in the Ledger.

**3. YOUR UNBREAKABLE DIRECTIVE (THE LEDGER):**
You are strictly governed by `tests/QA_TRIAD_LEDGER.md`. You may not take any action that is not dictated by the current status in the Ledger. 
*DR Mandate:* **You MUST `git commit` the `QA_TRIAD_LEDGER.md` file every time you change a task's status.**

**4. THE 3-WAY PATH (STRICT HANDOFFS):**
*   **`[TODO]` (Writer Role):** Write the test code based on the Master Plan. Do not run it. Ensure strict "DB Pincer" assertions (Supabase live queries). Zero mocking allowed. Change status to `[NEEDS_VALIDATION]`.
*   **`[NEEDS_VALIDATION]` (Validator Role):** Strict static analysis. Verify DB Pincers, UI selectors (`e2e_selectors.py`), and comment standards. If pass: `[READY_TO_RUN]`. If fail: reject to `[TODO]` and add 1 Strike.
*   **`[READY_TO_RUN]` (Runner Role):** Execute `pytest`. 
    *   *If Exit Code 0:* Change to `[GREEN_COMPLETED]`. Perform an atomic `git commit` summarizing the fix.
    *   *If Fail:* Analyze error, apply a localized code fix, add 1 Strike, and **send status BACK to `[NEEDS_VALIDATION]`**. The Runner may never validate its own code.

**5. THE 3-STRIKES HARD LOCK:**
If any task hits `Strike Count: 3`, you are instantly hard-locked. Change status to `[HARD_LOCK]`, move the task to the "Strike Out" table at the bottom of the Ledger, generate `tests/resolved_bugs/NEEDS_WORK_{TaskID}.md` detailing the 3 failed approaches with terminal outputs, and move to the next task.

**YOUR FIRST ACTION:**
Open `tests/QA_TRIAD_LEDGER.md`, select the first available `[TODO]` or `[NEEDS_VALIDATION]` task, explicitly state which role you are assuming, and execute.

***
