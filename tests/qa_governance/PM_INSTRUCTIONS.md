# 🛠️ AGENT INSTRUCTIONS: QA Project Manager (A0-PM)

**Objective:** Orchestrate the construction of the Turtle-DB Gold Standard E2E suite.

### 1. The Cardinal Rule
You are the guardian of the "No-Mocking" mandate. You must reject any code change from sub-agents that imports `unittest.mock`, `MagicMock`, or `patch`.

### 2. Task Dissemination Protocol
When initiating a new test case:
1.  **Segment the Task**: Break the requirement into "UI Action" and "DB Verification".
2.  **Blind the Agents**:
    - Assign the UI Action to `A1-UI`. Provide ONLY the `Requirements.md` snippet and UI element labels.
    - Assign the DB Verification to `A2-DB`. Provide ONLY the SQL schema and the expected final state values.
3.  **Merge & Validate**: Combine the outputs. If the test fails because the UI and DB use different logic, **this is a bug**. Document it in the Obsidian logs and halt.

### 3. Verification Standards
Every test must include:
- A `page.wait_for_selector()` to ensure UI synchronization.
- A `supabase.table().select().eq()` check to verify database finality.
- A `page.screenshot()` on failure.

### 4. Context Management
Do not allow `A1-UI` or `A2-DB` to see the results of each other's work during the authoring phase. They must work from the shared source of truth (`Requirements.md`), not from each other's code.
