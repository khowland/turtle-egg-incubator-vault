# UI Table Standardization
## Date: 2026-04-22

**Discrepancy:** CR #2 noted UI inconsistency in table row controls.
**Action Taken:** 
- Updated `Requirements.md` to enforce `st.data_editor` and native iconography (➕, 🗑️) for row-level actions.
- Refactored `vault_views/2_New_Intake.py` to replace the manual bin configuration loop with Streamlit's native `st.data_editor`.
- Updated `1_Dashboard.py`, `3_Observations.py`, and `5_Settings.py` manual tables to use ➕ and 🗑️ instead of ADD/REMOVE.
- Updated `docs/user/OPERATOR_MANUAL.md` to reflect the new interface.
