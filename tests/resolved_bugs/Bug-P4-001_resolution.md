---
component: "tests, vault_views"
issue_type: "fix"
resolved: true
---
# Bug Resolution: P4-001

## Discrepancy

- Test suite failures due to UI vocabulary missing allowed words (`WIPE` patterns, `DELETE` pattern).
- Legacy index-based test assumptions broken by the switch to `st.data_editor`.
- `NameError` on `mother_weight_g` in `2_New_Intake.py` from an incomplete previous patch.

## Action Taken

- Updated `tests/test_settings_and_help.py` to allow the new destructive action buttons and ➕/🗑️ emojis.
- Updated `test_audit_veracity.py`, `test_forensic_audit_payloads.py`, `test_red_team_intake.py` and `test_adversarial_persistence.py` to target `at.session_state.bin_rows[0]` directly rather than relying on non-existent `at.number_input`.
- Reconstructed `mother_weight_g`, `days_in_care`, and `carapace_length` definitions to `col2`/`col3` in `vault_views/2_New_Intake.py` ensuring variables referenced in the RPC are bound.

## Compliance

Tests pass with 100% success rate (66/66) excluding E2E. Db state mutation requirements and ui vocabulary requirements have been satisfied.
