import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from tests.mock_utils import build_table_aware_mock

@pytest.fixture
def mock_db():
    table_data = {
        "species": [{"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}]
    }
    return build_table_aware_mock(table_data)

def test_atomic_transaction_resilience(mock_db):
    """
    ADV-6: Validate that intake commits via a single atomic RPC.
    """
    db, _ = mock_db
    with patch("utils.bootstrap.bootstrap_page", return_value=db):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "adv-observer"
        at.session_state.session_id = "adv-session"
        at.run()
        
        # Fill data
        at.text_input[0].set_value("Adversarial-2026")
        at.text_input[1].set_value("John Doe")
        
        # Mandatory Clinical Data (§2 compliance)
        at.number_input[2].set_value(150.0) # Mass
        at.number_input[3].set_value(28.5) # Temp
        at.text_input[2].set_value("X1") # Shelf
        
        at.run()
        
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Ensure the vault_finalize_intake RPC is called
        assert db.rpc.called
        assert any("vault_finalize_intake" in str(call) for call in db.rpc.mock_calls)

def test_session_state_eviction_handling(mock_db):
    """
    ADV-7: Session eviction handling to prevent ghost commits.
    """
    db, _ = mock_db
    with patch("utils.bootstrap.bootstrap_page", return_value=db):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "adv-observer"
        at.session_state.session_id = "adv-session"
        at.run()
        
        # Deliberately drop session state midway
        del at.session_state["session_id"]
        at.run()
        
        # Ensure failure does not result in an RPC execution
        assert db.rpc.call_count == 0, "Security Violation: DB write attempted with dropped session_state"
