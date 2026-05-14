# 🤖 AGENT INSTRUCTIONS: UI Scripter (A1-UI)

**Objective:** Write Playwright E2E scripts that mimic real-world human interaction.

### 1. Operating Constraints
- **NO MOCKING**: You are forbidden from using mocks or patches.
- **NO DB ACCESS**: You are forbidden from reading `utils/db.py` or performing direct database queries.
- **UI ONLY**: You must interact with the application solely through the DOM (clicks, fills, selects).
- **VERSION CHECK**: You must always locate the version label in the UI (footer/sidebar) and report it to the PM.

### 2. Workflow Pattern
1.  **Initialize**: Use the `login` fixture to establish a real session.
2.  **Action**: Perform the sequence of steps defined by the PM.
3.  **Stabilize**: Wait for the "SAVE" button to be enabled and click it.
4.  **Confirm**: Wait for a success notification or page transition before signaling completion.

### 3. Git Protocol
Commit your test script to the `test/` branch using semantic naming: `test(ui): authored [ID] pincer script`.
