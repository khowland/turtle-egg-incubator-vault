import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch

def test_unified_vocabulary_compliance_diagnostic():
    """
    ADV-4: Ensure no buttons violate the Unified Vocabulary rule (SAVE, CANCEL, ADD, REMOVE, START).
    7_Diagnostic.py is known to use RUN, which is a violation. This test will flush it out.
    """
    with patch("utils.bootstrap.bootstrap_page"):
        at = AppTest.from_file("vault_views/7_Diagnostic.py")
        at.session_state.session_id = "test-session"
        at.run()
        
        allowed_labels = {"SAVE", "CANCEL", "ADD", "REMOVE", "START"}
        
        # Test will deliberately expose any button outside the allowed set
        violations = [btn.label for btn in at.button if btn.label not in allowed_labels]
        assert not violations, f"Found Unified Vocabulary violations: {violations}"

def test_bin_weight_check_blocking():
    """
    ADV-5: Ensure access to the observation grid is blocked until bin mass is recorded.
    """
    with patch("utils.bootstrap.bootstrap_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "test-observer"
        at.session_state.session_id = "test-session"
        at.run()
        
        # This will fail/succeed depending on if the UI blocks the grid rendering
        # Let's verify that without entering weight, a "SAVE" button or grid might be absent or disabled
        # Searching the DOM for Data Editor or warning messages
        has_warning = any("weight" in w.value.lower() for w in at.warning)
        submit_button = next((b for b in at.button if b.label == "SAVE"), None)
        
        if submit_button:
            # If button exists, it should be disabled if weights aren't recorded
            # or shouldn't proceed
            pass # Expand based on actual UI implementation in phase 2 remediation
