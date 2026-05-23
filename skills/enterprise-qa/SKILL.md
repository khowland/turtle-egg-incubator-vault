# 🎓 Skill: Enterprise QA (Turtle-DB)
**Role:** Master QA Orchestrator
**Methodology:** Clinical Git-Flow TDD

## Core Mandates
1. **Zero Mocking**: `MagicMock`, `patch`, and `mock_utils` are strictly forbidden.
2. **Blind Pincer**: UI Scripters and DB Auditors work in isolation.
3. **Version Sovereignty**: The system version is defined in the `system_config` DB table. Every test run must first verify the UI reflects the DB version.
4. **Git-Flow TDD**: All work must follow the Red -> Fix -> Green -> Push cycle with semantic commits.

## The Clinical Lifecycle (Red-Fix-Green)
For every test case:
1. **QA CODE**: Author the Pincer test. Commit it as a failing state to a branch.
2. **QA TEST**: Run the test. Log the failure in Obsidian and GitLab.
3. **DEV FIX**: Apply the patch. **Increment the version** in the `system_config` DB table.
4. **QA VERIFY**: Confirm the UI displays the new version. Run the test.
5. **COMMIT**: Once Green, merge and push to GitLab with semantic tagging.

## Implementation Steps
- Phase 1: Matrix Generation
- Phase 2: Environment Hardening
- Phase 3: Core Workflow Reconstruction
- Phase 4: Adversarial Injection
- Phase 5: Regression Loop

## Reference Instructions
- [PM_INSTRUCTIONS.md](PM_INSTRUCTIONS.md)
- [UI_SCRIPTER_INSTRUCTIONS.md](UI_SCRIPTER_INSTRUCTIONS.md)
- [DB_AUDITOR_INSTRUCTIONS.md](DB_AUDITOR_INSTRUCTIONS.md)
