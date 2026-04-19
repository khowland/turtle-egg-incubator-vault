# Token Budget Optimization Protocol for Autonomous Streamlit QA

**Objective:** To establish rigid constraints for the QA and Debugging lifecycle that maximize token efficiency and minimize cloud inference costs without sacrificing accuracy.

While the "Pre-Flight Analysis" methodology is vastly superior to blind UI interaction, it introduces its own token vulnerabilities if executed naively. Below is the re-examined methodology applying strict token conservation protocols.

---

## 1. Phase 1: Mitigating Context Ingestion Risks

**The Vulnerability:** "Read `requirements.md` and the full codebase." 
If the Streamlit application consists of 50 files and 20,000 lines of code, passing the entire repository into the Phase 1 generation prompt will consume a massive token budget and induce the "Needle-in-a-Haystack" accuracy drop where the LLM forgets instructions midway through.

**The Optimized Protocol:**
*   **Targeted Retrieval Instead of Bulk Ingestion:** The Phase 1 Planning Agent MUST be prohibited from bulk file reading. Instead, it must be constrained to use Semantic Search (`codebase_search`), AST parsing, or `grep_search`. 
*   **Workflow:** 
    1.  Agent reads `requirements.md`.
    2.  Agent performs a `grep` for `st.session_state` and `st.button` specifically to map the active state mutations.
    3.  Agent only pulls the specific components that match the requirements.
*   *Token Savings:* Eliminates processing tens of thousands of tokens of static utility code that is irrelevant to the UI state testing.

## 2. Phase 2: Optimizing Playwright DOM Ingestion

**The Vulnerability:** Running E2E tests using Playwright. 
When a Playwright test fails because a Streamlit element didn't appear, the default behavior of many agents is to ask for `page.content()`. A raw Streamlit UI DOM can easily exceed 50,000 text tokens due to inline React wrappers and base64 strings, instantly skyrocketing the API bill.

**The Optimized Protocol:**
*   **Semantic Compaction via Ingestion Tools:** Never allow the agent to read the raw HTML DOM. 
*   **Workflow:** When the execution script fails, the testing framework MUST pipe the DOM through `Crawl4AI` (or `Browser-use` Accessibility Trees). These tools aggressively strip CSS, `<script>` tags, and visual wrappers, returning only bare-metal Semantic Markdown. 
*   *Token Savings:* Compresses a 50k token HTML payload down to a manageable 1k–3k token Markdown payload, providing the exact same functional context to the LLM.

## 3. Phase 3: The "Single-File Patch" Rule

**The Vulnerability:** The Coding Agent trying to fix a bug while holding the entire testing suite and the entire application state in memory simultaneously.

**The Optimized Protocol:**
*   **Architectural Blinders:** Once the Bug Ticket is generated, the Coding Agent is assigned to fix it. The agent must operate under the **"Single-File Patch Rule."**
*   **Workflow:** If the bug is mapped to `auth_module.py`, the agent is ONLY allowed to load `auth_module.py` and the 15-line `pytest` failure log. It is explicitly banned from reading the frontend layout files or the entire test suite. 
*   *Token Savings:* Keeps the context payload localized purely to the mutating logic, eliminating the tax of carrying the full application context into every debugging loop.

---

## Conclusion
By shifting from "Bulk Ingestion" to "Targeted Retrieval" (Search) and from "Raw HTML" to "Semantic Ingestion" (Crawl4AI), the methodology retains absolute Sovereign QA confidence while drastically lowering the per-loop token burn, protecting the API budget across long development lifecycles.

## 3. Phase 3: QA State Rehydration (Red Team Validation)
To properly validate complex mid-season UI workflows without incurring massive token costs or manual data entry overhead, QA must utilize the Administrative Database State mechanisms defined in the requirements.

### 3.1 Targeted State Provisioning
Instead of blindly manipulating the UI step-by-step to create complex clinical scenarios (which explodes the context window), QA tests should:
1.  Invoke the Mid-Season Data state (`State 2`) via the secure API/RPC prior to testing.
2.  Validate the specific clinical workflow (e.g., advancing a pre-seeded S5 egg to S6) against this known baseline.
3.  Revert the system to the Clean Deployment state (`State 1`) upon completion.

### 3.2 UI Security & Backup Validation
When performing QA on the Settings menu Backup/Restore logic:
*   **Negative Testing Protocol**: The agent MUST verify that the Restore/Seed options are functionally locked if a mandatory backup has not been executed on a populated database.
*   **Timestamp Fuzzing**: The QA agent MUST attempt to maliciously inject past system dates into `intake_timestamp` or `created_at` payloads to ensure the backend constraints successfully override them with `now()`, guaranteeing the integrity of the audit logs against UI tampering.
