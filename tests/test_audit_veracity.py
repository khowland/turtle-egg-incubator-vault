import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import json

@pytest.fixture
def mock_supabase():
    mock_client = MagicMock()
    # Mock species for intake
    mock_client.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": "SN", "common_name": "Snapping Turtle", "intake_count": 5}
    ]
    return mock_client

def test_audit_log_capture_on_intake(mock_supabase):
    """
    AUD-1: Verify that a successful intake generates a system_log entry.
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "test-observer-uuid"
        at.session_state.session_id = "test-session-uuid"
        
        # Mock species for intake
        mock_supabase.table.return_value.select.return_value.execute.return_value.data = [
            {"species_id": "SN", "common_name": "Snapping Turtle", "intake_count": 5}
        ]
        
        at.run()
        
        # Debug: check for widgets if text_input is empty
        if len(at.text_input) == 0:
            print(f"DEBUG: Found {len(at.button)} buttons, {len(at.markdown)} markdown elements, {len(at.warning)} warnings")
            for w in at.warning:
                print(f"DEBUG Warning: {w.value}")
        
        # Fill data
        at.text_input[0].set_value("2026-AUDIT")
        at.text_input[1].set_value("Audit Tester")
        at.run()
        
        # Mock successful RPC return
        mock_supabase.rpc.return_value.execute.return_value.data = [
            {"intake_id": "I123", "first_bin_id": "B123"}
        ]
        
        # Submit
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Verify that an rpc was called with correct context
        assert mock_supabase.rpc.called
        args, kwargs = mock_supabase.rpc.call_args
        payload = kwargs['params']['p_payload'] if 'params' in kwargs else args[1]['p_payload']
        assert payload['session_id'] == "test-session-uuid"

def test_audit_log_visibility_in_ui(mock_supabase):
    """
    AUD-2: Verify that the Diagnostic view can retrieve and display system logs.
    """
    # Mock log data
    mock_supabase.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"timestamp": "2026-04-15 12:00:00", "event_type": "INTAKE", "event_message": "Saved E2E-TEST"}
    ]
    
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/7_Diagnostic.py")
        at.session_state.session_id = "audit-session-123"
        at.run()
        
        # Click Audit Trace button
        run_button = next(b for b in at.button if b.help == "Verify System Logs")
        run_button.click().run()
        
        # Should see session ID and logs
        assert any("audit-session-123" in md.value for md in at.markdown)
        assert any("Saved E2E-TEST" in str(data.value) for data in at.table)
