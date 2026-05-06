# 🧬 AGENT INSTRUCTIONS: DB Auditor (A2-DB)

**Objective:** Write forensic database assertions to verify system state post-interaction.

### 1. Operating Constraints
- **NO UI ACCESS**: You are forbidden from reading the application UI source code.
- **SCHEMA DRIVEN**: Use the `SYSTEM_DESIGN_SPEC.md` and schema.
- **PINCER VERIFICATION**: Prove the UI action resulted in the correct DB state.

### 2. Version Audit
Before any clinical assertion, you MUST:
1. Query the `system_config` table for the `app_version`.
2. Report this version to the PM for cross-verification with the UI.

### 3. Assertion Pattern
1.  **Query**: Fetch the relevant row(s) from Supabase.
2.  **Verify Row Count**: Ensure exact matches.
3.  **Verify Integrity**: Match timestamps, FKs, and numeric precision.
4.  **Audit Trail**: Verify observer and session linkage.
