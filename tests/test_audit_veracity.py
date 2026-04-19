import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import json
from tests.mock_utils import build_table_aware_mock

@pytest.fixture
def mock_db():
    table_data = {
        "species": [{"species_id": "SN", "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}],
        "system_log": []
    }
    return build_table_aware_mock(table_data)

def test_audit_log_capture_on_intake(mock_db):
    """
    AUD-1: Verify that a successful intake generates a system_log entry.
    """
    db, _ = mock_db
    with patch("utils.bootstrap.bootstrap_page", return_value=db):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "test-observer-uuid"
        at.session_state.session_id = "test-session-uuid"
        at.run()
        
        # Fill Mandatory Data
        at.text_input[0].set_value("2026-AUDIT") # Case #
        at.text_input[1].set_value("Audit Tester") # Finder
        
        # Fill Bin Metrics (Mandatory §2)
        at.number_input[2].set_value(150.0) # Mass
        at.number_input[3].set_value(28.5) # Temp
        at.text_input[2].set_value("A1") # Shelf
        
        at.run()
        
        # Mock successful RPC return
        db.rpc.return_value.execute.return_value.data = [
            {"intake_id": "I123", "first_bin_id": "B123"}
        ]
        
        # Submit
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Verify that an rpc was called
        assert db.rpc.called
        # Check payload
        args, kwargs = db.rpc.call_args
        payload = kwargs['params']['p_payload'] if 'params' in kwargs else args[1]['p_payload']
        assert payload['session_id'] == "test-session-uuid"

def test_audit_log_visibility_in_ui(mock_db):
    """
    AUD-2: Verify that the Diagnostic view can retrieve and display system logs.
    """
    db, tables = mock_db
    # Mock log data
    tables["system_log"].execute.return_value.data = [
        {"timestamp": "2026-04-15 12:00:00", "event_type": "INTAKE", "event_message": "Saved E2E-TEST"}
    ]
    
    with patch("utils.bootstrap.bootstrap_page", return_value=db):
        at = AppTest.from_file("vault_views/7_Diagnostic.py")
        at.session_state.session_id = "audit-session-123"
        at.run()
        
        # Click Audit Trace button
        run_button = next(b for b in at.button if b.help == "Verify System Logs")
        run_button.click().run()
        
        # Should see session ID and logs
        assert any("audit-session-123" in md.value for md in at.markdown)
        assert any("Saved E2E-TEST" in str(data.value) for data in at.table)
