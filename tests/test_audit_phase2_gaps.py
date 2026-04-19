import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import os

def test_gap_intake_weight_bypass():
    """[B-001] Verify that Intake allows saving without weight recording."""
    at = AppTest.from_file("vault_views/2_New_Intake.py", default_timeout=5)
    at.session_state.observer_id = "test-biologist"
    at.session_state.session_id = "test-session"
    at.run()
    
    # Access widgets by searching the label property
    finder_input = next(i for i in at.text_input if "found" in i.label.lower())
    case_input = next(i for i in at.text_input if "Case #" in i.label)
    
    finder_input.set_value("Tester")
    case_input.set_value("2026-TEST")
    
    # Check if there is ANY weight input in the bin rows
    # Based on audit, weight/mass labels are missing
    weight_inputs = [i for i in at.number_input if "weight" in i.label.lower() or "mass" in i.label.lower()]
    assert len(weight_inputs) == 0, "Weight input found in Intake! Audit suggests it was missing."
    
    # Attempt to SAVE - it should proceed to RPC if validation passes
    save_btn = next(b for b in at.button if b.label == "SAVE")
    assert not save_btn.disabled, "SAVE button should be enabled even without weight (the bug we are auditing)"

def test_gap_session_undefined_client():
    """[B-004] Verify the NameError bug in session.py via source analysis simulation."""
    # The bug is evident in the source: session.py uses 'supabase_client' which is not in scope
    with open("utils/session.py", "r") as f:
        source = f.read()
        # Check if 'supabase_client' is used in show_splash_screen without being defined
        assert "get_resilient_table(supabase_client," in source
        # Find the start of show_splash_screen and ensure no local definition exists before usage
        splash_part = source.split("def show_splash_screen")[1].split("def ")[0]
        assert "supabase_client = get_supabase()" not in splash_part, "Bug B-004: supabase_client is used but not defined in local scope."

def test_mobile_column_ratios():
    """[E-003] Audit column ratios for mobile compatibility."""
    with open("vault_views/2_New_Intake.py", "r") as f:
        content = f.read()
        # Standard mobile displays struggle with columns < 1/4 width
        assert "st.columns([2, 1, 1])" in content, "Intake uses cramped 3-column layout (2:1:1) which is poor for mobile."
