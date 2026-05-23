# Root Cause Analysis (RCA): Phase 3/4 Debugging Session

## 1. Failure Categories

### A. Brittle AppTest Scripts (70% of failures)
- **Selectbox vs. Checkbox**: Tests were looking for checkboxes in standard grid mode, but the view had pivoted to "Correction Mode" (Surgical Resurrection) which uses a selectbox for egg selection.
- **Dynamic Labels**: Labels with emojis or state-aware prefixes (e.g., `✅ Status` vs `➖ Status`) caused `next()` lookups to fail in tests that used exact label matching.
- **Mock Chaining Collisions**: Using a single `MagicMock` for all database tables caused queries to one table to overwrite the configuration of another, leading to `IndexError` or `AssertionError` in downstream operations.

### B. Systemic UI Gaps (20% of failures)
- **Sidebar Absence**: The `render_custom_sidebar()` function was defined but never called in the view-bootstrap layer, leading to the "SHIFT END" button being missing on all clinical screens.
- **Branding Violations**: Ad-hoc buttons were missing the required `type="primary"` token for Green-theme compliance.

### C. Clinical Logic Edge Cases (10% of failures)
- **S6 Rollback Orphans**: Rollbacks from Hatching (S6) require atomic voiding of both the egg observation and the hatchling ledger entry to prevent data artifacts.

## 2. Zero-Defect Resonance Strategy

- [x] **Universal Mocking**: Use `build_table_aware_mock` in `tests/mock_utils.py` to isolate table queries.
- [ ] **Methodology**: Update `Requirement.md` or `workspace_context.md` with "Test Strategy: AppTest Best Practices".
- [ ] **Flagging**: Any repetitive failure (e.g., "button not found") now triggers an immediate manual inspection of the `vault_views/` logic before test modification.
- [ ] **Verification**: Every fix must be followed by a focused regression of that specific module PLUS a full suite run.
