import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import os

def test_gap_intake_weight_bypass():
    """[B-001] Verify that Intake now REQUIRES weight recording (Hardened)."""
    at = AppTest.from_file("vault_views/2_New_Intake.py", default_timeout=5)
    at.session_state.observer_id = "test-biologist"
    at.session_state.session_id = "test-session"
    at.run()
    
    # Check if there is a weight/mass labeled input now
    weight_inputs = [i for i in at.number_input if "weight" in i.label.lower() or "mass" in i.label.lower()]
    assert len(weight_inputs) > 0, "Hardening Failure: Weight input not found in Intake!"

def test_gap_session_undefined_client():
    """[B-004] Verify the fix for NameError in session.py via source analysis."""
    # Use UTF-8 for Windows compatibility (B-004 remediation)
    with open("utils/session.py", "r", encoding="utf-8") as f:
        source = f.read()
        # Find the start of show_splash_screen
        splash_part = source.split("def show_splash_screen")[1].split("def ")[0]
        # Verify the fix is present
        assert "supabase_client = get_supabase()" in splash_part, "Fix Verification: supabase_client must be defined in local scope."

def test_mobile_column_ratios():
    """[E-003] Audit column ratios for mobile compatibility."""
    with open("vault_views/2_New_Intake.py", "r", encoding="utf-8") as f:
        content = f.read()
        # Ensure we haven't reverted to cramped ratios
        assert "st.columns([1, 1, 2])" in content or "st.columns([2, 1, 1])" in content
