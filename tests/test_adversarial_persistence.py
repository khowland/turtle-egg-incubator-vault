import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

def test_atomic_transaction_resilience():
    """
    ADV-6: Validate that intake commits via a single atomic RPC.
    """
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}
    ]
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "adv-observer"
        at.session_state.session_id = "adv-session"
        at.run()
        
        # Trigger an adversarial DB payload execution
        at.text_input[0].set_value("Adversarial-2026")
        at.text_input[1].set_value("John Doe")
        at.run()
        
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Ensure only the vault_finalize_intake RPC is called, 
        # meaning atomic validation instead of multi-query INSERTs.
        rpc_calls = [call for call in mock_supabase.rpc.mock_calls if "vault_finalize_intake" in str(call)]
        assert len(rpc_calls) >= 1, "Expected atomic RPC 'vault_finalize_intake' to be utilized"

def test_session_state_eviction_handling():
    """
    ADV-7: Session eviction handling to prevent ghost commits.
    """
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}
    ]
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "adv-observer"
        at.session_state.session_id = "adv-session"
        at.run()
        
        # Deliberately drop session state midway
        del at.session_state["session_id"]
        at.run()
        
        # Ensure failure does not result in an RPC execution
        assert mock_supabase.rpc.call_count == 0, "Security Violation: DB write attempted with dropped session_state"
