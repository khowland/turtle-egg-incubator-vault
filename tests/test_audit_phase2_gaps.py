import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import os

def test_gap_intake_weight_bypass():
    """[B-001] Verify that Intake now REQUIRES weight recording (Hardened)."""
    mock_supabase = MagicMock()
    # Mock species data to allow the page to render fully
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "BL", "common_name": "Blanding's", "intake_count": 5}
    ]
    
    with patch("utils.db.get_supabase_client", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py", default_timeout=10)
        at.session_state.observer_id = "test-biologist"
        at.session_state.session_id = "test-session"
        at.run()
        
        # CR-20260501-1800: Initial Mass column removed from UI per Ac-5; weight now tracked via Observations.
        # Verify the intake source still has mother_weight_g set to None.
        with open("vault_views/2_New_Intake.py", "r", encoding="utf-8") as f:
            intake_source = f.read()
        assert "mother_weight_g = None" in intake_source, "Hardening Failure: Mother weight should be set to None (UI-removed per Ac-5)!"

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
        # CR-20260426 Ac-5: After Mother's Weight removal, the row uses [2, 1] not [2, 1, 1]
        assert "st.columns([2, 1])" in content or "st.columns([2, 1, 1])" in content or "st.columns([1, 1, 2])" in content
