# Red Team Adversarial Review — System Alignment Check Draft

**Red Team Adversarial Review — System Alignment Check Draft**

## Critical Findings (Must address before approval)

### CF-1: Missing Core Alignment Dimensions
The report assesses test coverage and performance, but completely omits evaluation of other critical system objectives from `Requirements.md` and `implied_system_objective.md`:
- **Data Privacy & RBAC**: No mention of testing role-based access controls (Observer vs Admin vs Researcher), data export restrictions, or compliance with privacy requirements.
- **Security Adversarial Testing**: Beyond stage jump blocking, there are no adversarial tests for SQL injection, XSS, session hijacking, or input validation attacks in intake forms.
- **Clinical Data Lineage**: Audit trail completeness is claimed as gap-closed, but no verification that `modified_by_id` is correctly set on all observation updates (e.g., during weight gate changes, stage progressions, or corrections).
- **Disaster Recovery**: Crash recovery is noted as “no change needed” but no test of backup restoration, ledger replay, or data consistency post‑recovery has been performed.
- **Scalability Beyond 50 Items**: The report treats TSK‑07 (50‑observation loop) as sufficient, but real‑world clinical workflows may generate hundreds of bins per season. No plan for stress testing at higher volumes or multi‑user contention.
- **User Acceptance & Usability**: No feedback loop for the emoji heading decision (D2); if users depend on visual cues, delaying this after all technical work may cause dissatisfaction.

**Recommendation:** Add a new section 3.x “Other Alignment Objectives” listing each missing domain with status and planned tests. Do not approve without at least scoping these items.

### CF-2: Unrealistic Risk Assessment Table (Section 5)
The table lists only three risks, all focused on test execution failures. Many high‑probability/high‑impact risks are omitted:
- Regressions in observation stage logic due to schema changes (`modified_at`, `observer_id`) – likelihood **medium**, impact **high** (failure of all observation tests).
- Test flakiness from factory fixture absence (Cat‑B) – likelihood **high**, impact **medium** (unreliable test results, wasted cycles).
- Data corruption from concurrent observation saves (multi‑session) – likelihood **low**, impact **critical** (clinical data integrity).
- Dependency on external Supabase availability (network failure) – likelihood **low**, impact **medium** (CI delays).

**Recommendation:** Expand the risk matrix to at least 8 items with realistic likelihood and impact ratings. Re‑evaluate before executing any action.

### CF-3: QA Methodology Violation – KB‑First Rule Disregarded
The report defers documentation updates (D1) to the very end (priority 0.67). The QA methodology calls for “KB‑First Rule: Always search 00_CENTRAL_HUB.md and resolved bugs before investigating failures.” Updating the Central Hub and ledger with current state (e.g., reopened tasks, closed CRs) is a prerequisite for any agent to execute the next actions safely. Skipping this risks tasks running with stale status causing conflicting modifications.

**Recommendation:** Move D1 to the Immediate section (priority = highest). Update `00_CENTRAL_HUB.md` and `QA_TRIAD_LEDGER.md` before any code changes.

### CF-4: Assumptions Requiring Testing Before Action
- **A2 (Run TSK‑04) assumes schema changes do not break observation workflows** – no evidence. The test was last run before `modified_at` and `observer_id` were added to `bin_observation` and `session_log`. The new columns may cause unexpected form errors or mismatch in `number_input` bindings. Must verify by a dry‑run or unit test first.
- **A4 (Adversarial tests) assumes stage jump enforcement covers all non‑sequential transitions** – but the biological state machine allows certain backward transitions (e.g., S5→S1 for surgical corrections). The test must verify that the “surgical_resurrection” flag permits legit corrections while still blocking arbitrary jumps. The report acknowledges this but does not specify test scope for flag‑based exceptions.
- **B2 (Test data factory) assumes UI‑based factory can generate bins in isolation** – but current intake flow requires a season to be “active” and species list valid. Season state may need pre‑seeding, not covered.

**Recommendation:** Add an “Assumptions to Validate” subsection before launching any action. Write quick smoke tests (e.g., a small Python script hitting the Supabase API) to verify column presence and default values.

---

## Major Suggestions (Strongly recommended changes)

### S1: Reprioritize Immediate Actions
Current order A1‑A2‑A3‑A4 is suboptimal:
- **A1 (TSK‑03 rewrite) should be executed first**, as it unblocks multiple tests and removes stale selector dependencies.
- **A4 (adversarial tests for stage jumps) should run before A2 (TSK‑04 ordinary workflows)**, because adversarial tests often expose hidden flaws that ordinary workflows might mask. If stage jump enforcement is buggy, A2 may pass but later crash on real data.
- **A3 (scalability) can be deferred after A2 passes**; scalability testing is less urgent than core workflow validation.

Suggested order: **A1 → A4 → A2 → A3**. Adjust effort and priority scoring accordingly.

### S2: Embed Triad Handoff Checks in Every Action
The report mentions Triad handoffs for A1 and A4 but not for A2, A3, B1‑B3. The QA governance requires Writer → Validator → Runner for any test code change. For “just run” actions, at minimum a Validator should perform a static analysis of the test file before execution to confirm no missing imports or signature issues. Failure to enforce this may lead to wasted runs and unnecessary strikes.

**Recommendation:** Add a “Triad Gate” column in the action table indicating required handoffs for each item.

### S3: Add a Regression Suite Phase Before Full Suite Run (B3)
The report plans B3 (full suite run) only after B1 and B2. However, incremental regression runs of just the observation‑related tests after A2 and A4 would catch schema‑related regressions earlier and avoid a large untriaged log dump later. Add a **B0‑Regression Gate** step: after A2 and A4 pass, run all observation tests (`test_observation_workflows.py`, `test_adversarial_forensic.py`, `test_surgical_corrections.py`, `test_observations_e2e.py`) before proceeding to B1.

### S4: Incorporate Security & RBAC Testing as Immediate Priority
Given the application handles sensitive clinical data, a lack of adversarial security testing is a serious gap. Propose a new immediate action **A5: RBAC Smoke Test** – verify that Observer role cannot access Settings/Admin pages, and that SQLi payloads in intake fields are sanitized. This aligns with enterprise QA mandate of adversarial resilience.

---

## Minor Nits

- **Section 3 “User‑Facing Bin Identifiers” gap labeled “Minor”** is actually **Moderate** – error messages that leak internal `bin_id` can confuse support staff and violate clean UI principles. Should be raised to a P2 fix.
- **A2 effort score of 2 is too low** – even if the test passes, validation of output, parsing logs, and updating the ledger will take more time; a realistic effort is 3‑4.
- **D2 “Emoji Heading Decision” suggests Option B but does not include verification step** – needs a test to confirm that adding emojis back does not break `e2e_selectors` (should be trivial but must be checked).
- **Section 4.3 table missing B1 entry** – B1 is listed in 4.2 but not in priority table, inconsistency.

---

## Overall Assessment

**Status: Needs Major Revision**

The report correctly identifies test‑suite blockers and sketches a path to stabilize E2E coverage. However, it fails to assess critical non‑functional requirements (security, privacy, RBAC, data lineage verification), underestimates risks, violates the KB‑first governance rule, and presents an action sequence that may mask regressions. The risk matrix is dangerously narrow. I cannot recommend approval until CF‑1, CF‑2, CF‑3, and CF‑4 are addressed, and the prioritization changes (S1, S2) are incorporated. A second review after revision is required.
