import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

def test_button_label_and_type_compliance():
    """
    ADV-11: Verify buttons use standard labels and appropriate 'primary' types.
    While AppTest cannot easily check the computed CSS color, we can assert 'type'
    and labels match the WINC design tokens.
    """
    with patch("utils.bootstrap.bootstrap_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "test-user"
        at.session_state.session_id = "test-session"
        at.session_state.workbench_bins = {"TEST-BIN"}
        at.session_state.env_gate_synced = {"TEST-BIN": True}
        at.run(timeout=10)
        
        save_buttons = [b for b in at.button if b.label == "SAVE"]
        for btn in save_buttons:
            # SAVE must be primary (to trigger the Green theme color if configured)
            assert btn.type == "primary", f"SAVE button {btn.key} is not 'primary' type as required for Green branding."

        # Check for non-standard labels in observations (should only be SAVE, CANCEL, ADD, REMOVE, START)
        allowed = {"SAVE", "CANCEL", "ADD", "REMOVE", "START"}
        violations = [b.label for b in at.button if b.label not in allowed]
        # Note: Some buttons might have dynamic labels if not careful.
        # Currently, 3_Observations.py has 'START' (Line 526)
        assert not violations, f"Branding Violation: Found non-standard button labels: {violations}"
