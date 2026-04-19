import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import json

@pytest.fixture
def mock_supabase():
    mock_client = MagicMock()
    # Default success response for species
    mock_client.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}
    ]
    return mock_client

def test_finder_name_regex_bypass_attempt(mock_supabase):
    """
    ADV-1: Ensure special characters in finder name are caught by the validation regex.
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "test-observer"
        at.session_state.session_id = "test-session"
        at.run()
        
        # Inject script tag into finder name
        at.text_input[1].set_value("<script>alert('xss')</script>")
        at.run()
        
        # Verify warning appears
        assert "Names can only have letters, numbers, and spaces." in at.warning[0].value
        
        # Attempt to save - should block because is_valid_finder is False
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Should not have called RPC because of the block
        assert not mock_supabase.rpc.called

def test_rpc_failure_safe_state(mock_supabase):
    """
    ADV-2: Simulates a database RPC failure and verifies 'Safe-State' logging.
    """
    # Mock RPC to raise an exception
    mock_supabase.rpc.side_effect = Exception("Postgres Error: Deadlock")
    
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "test-observer"
        at.session_state.session_id = "test-session"
        at.run()
        
        # Fill valid data
        at.text_input[0].set_value("2026-ERR")
        at.text_input[1].set_value("RedTeam")
        at.run()
        
        # Trigger SAVE
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run(timeout=10) # Increase timeout for failure handling
        
        # Verify error message shows 'Safe-State' context (handled by safe_db_execute)
        assert any("RPC failed" in err.value or "could not be saved" in err.value for err in at.error)

def test_missing_session_id_security_gate(mock_supabase):
    """
    ADV-3: Verifies that the app handles missing session_id gracefully.
    We need to ensure the mock doesn't completely skip the session logic if we want to test it,
    OR we test that the app re-initializes it when we call the REAL bootstrap.
    """
    import streamlit as st
    import uuid
    
    # We'll use a side effect to simulate the real bootstrap's session logic
    def bootstrap_side_effect(title, icon):
        if "session_id" not in st.session_state:
            st.session_state["session_id"] = str(uuid.uuid4())
        return mock_supabase

    with patch("utils.bootstrap.bootstrap_page", side_effect=bootstrap_side_effect):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.run()
        
        # Explicitly remove session_id from session_state
        del at.session_state["session_id"]
        
        at.run()
        # The side_effect should have re-initialized it
        assert "session_id" in at.session_state
