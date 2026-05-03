# 🏛️ FINAL MASTER PLAN: Enterprise QA & Integration Standard

**Classification:** Immutable Core Directive
**Project:** Turtle-DB (WINC)
**Objective:** Execute a near-zero defect QA overhaul in a time-compressed window, ensuring 100% forensic data integrity, strict UI-to-Database validation, and resilience against adversarial inputs.

---

## 1. 🎯 The Mission & Core Mandates
All QA engineers and sub-agents are bound by these absolute directives:
1. **Zero Mocking Tolerance:** `MagicMock` and `patch` are strictly forbidden for database operations. All tests must read/write to a live, local Supabase instance.
2. **True Human Simulation:** Every test must interact with the application solely through the UI (clicks, typing). Direct programmatic mutation of state (e.g., modifying `session_state`) is banned.
3. **The DB Pincer Validation:** A test passes *only* if a subsequent database query proves the UI action resulted in the exact expected row accumulation and timestamp sovereignty.
4. **Adversarial Resilience:** For every "Happy Path" test, there must be a corresponding negative test attempting to break the system (e.g., negative mass, chronological paradoxes).

---

## 2. ⚙️ Hardware & Sub-Agent Optimization (M6800 Standard)
Given the hardware constraints of the Dell M6800, execution must be highly optimized:
1. **Strict Sequential Execution:** Playwright E2E tests must never run in parallel (`pytest -n 1`). 
2. **Headless Execution:** Playwright must run in Headless mode to conserve GPU/CPU cycles.
3. **Sub-Agent Compartmentalization:** AI agents must not be fed the entire codebase. Agents will be assigned micro-tasks via Obsidian tickets (e.g., "Agent 1: Read View X, write Playwright script. Agent 2: Read DB Schema, write Assertions").

---

## 3. 🛡️ The Obsidian Protocol (Anti-Looping)
To prevent infinite testing loops and endless repeated fixes:
1. **Document Before Fixing:** When a test fails, code changes are forbidden until the failure is logged in Obsidian.
2. **The Entry:** Log the Error, the Root Cause, and the Proposed Fix.
3. **Reevaluation Check:** The developer/agent must read previous Obsidian logs. If the proposed fix failed previously, they must formulate a new architectural approach.
4. **Final Log:** Update the Obsidian ticket with the Success/Failure of the fix.

---

## 4. 🚀 The 5-Phase Time-Sensitive Execution Timeline

### Phase 1: Test Case Audit & Matrix Generation (Documentation Only)
*   **Action:** Do not write executable code. Map every UI element across the system to a written test case in a Master Test Matrix (Happy Path + Adversarial).
*   **Current Status:** *Intake Workflow Matrix Generated. Observation Matrix Pending.*

### Phase 2: Environment Hardening & Mock Purge
*   **Action:** Spin up the minimal local Supabase PostgreSQL container. Eradicate all `unittest.mock` imports from the clinical testing suite. 

### Phase 3: Core Workflow Reconstruction (The Gold Standard)
*   **Action:** Write Playwright scripts for the Phase 1 matrices. 
*   **Execution Pattern:** Execute the UI -> Wait for Success Toast -> Execute `get_supabase().table().select()` -> Assert row counts and timestamps.
*   **Template Provided:** `test_enterprise_intake.py` serves as the immutable template for all future scripts.

### Phase 4: Adversarial & Stress Testing
*   **Action:** Write the Playwright scripts that inject Hostile Inputs (e.g., empty strings, future dates, negative numbers).
*   **Validation:** Assert that the UI gracefully rejects the input AND that the database remained pristine (`COUNT()` did not increase).

### Phase 5: Mid-Season Scalability (Scheduled Run)
*   **Action:** Loop the Phase 3 workflows 50+ times to simulate massive data entry over time.
*   **Hardware Constraint:** Schedule this run during off-hours to prevent M6800 bottlenecking. Perform a final mathematical audit on total egg counts vs active database rows.

---

**[END OF MASTER PLAN]**
