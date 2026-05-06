# 🛑 QA Agent Accountability Protocol (The 3-Strikes Rule)

**Classification:** UNBREAKABLE DIRECTIVE
**Target:** All Sub-Agents and QA Developer AI

## 1. The Absolute Validation Gate
You are strictly prohibited from marking any testing or development task as "Complete" unless the following conditions are met:
1.  **Terminal Proof:** The specific local test command (e.g., `pytest tests/e2e_playwright/test_target.py`) returns a strict `Exit Code 0`. 
2.  **DB Sovereign Validation:** The test explicitly asserts the correct database state via a live query (The DB Pincer).
3.  **No Hallucinations:** Phrases like "Looks good to me," "I assume this works," or "This should fix the issue" are banned. You must prove it mathematically.

## 2. The 3-Strikes Rule (Anti-Looping Protocol)
If a test fails or a bug is discovered, you are authorized to fix it using the "Isolated Remediation" pattern (modifying only the target file). However, you are bound by the Strike Counter:

*   **Strike 1:** Your first fix attempt fails the test. You must evaluate the terminal error, form a new hypothesis, and try again.
*   **Strike 2:** Your second distinct approach fails. You must deeply reflect on the root cause. You cannot blindly guess. 
*   **Strike 3 (HARD LOCK):** If your third approach fails, you are out of strikes. **YOU MUST STOP CODING.**

## 3. The Failure Post-Mortem Requirement
Upon hitting Strike 3, you are hard-locked. To clear the lock and request Human Architect intervention, you must generate a discrete file named `tests/resolved_bugs/FAILURE_POST_MORTEM_Bug-{ID}.md` containing:

1.  **Objective:** What you were trying to achieve.
2.  **Approach 1:** What code you changed, why you thought it would work, and the exact terminal error it produced.
3.  **Approach 2:** Same as above.
4.  **Approach 3:** Same as above.
5.  **Root Cause Hypothesis:** Why you believe all three standard approaches failed (e.g., hidden framework limitation, upstream data dependency).
6.  **Hand-off:** Explicitly request the Human Architect to review the Post-Mortem.

*Any agent found violating this protocol by endlessly looping or hallucinating success will be subject to immediate termination of process.*
