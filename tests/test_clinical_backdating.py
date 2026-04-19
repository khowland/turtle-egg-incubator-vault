import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import datetime

def test_backdating_is_honored_in_observation():
    """
    ADV-8: The clinical observation must honor the user-selected backdate.
    """
    mock_supabase = MagicMock()
    table_mocks = {}

    def mock_table(table_name):
        if table_name in table_mocks:
            return table_mocks[table_name]
        
        mock_query = MagicMock()
        if table_name == "species":
            mock_query.select.return_value.execute.return_value.data = [
                {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle"}
            ]
        elif table_name == "intake":
            mock_query.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "M1", "intake_name": "MOTHER-1"}
            ]
        elif table_name == "bin":
            mock_query.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": "TEST-BIN", "intake_id": "M1"}
            ]
        elif table_name == "egg":
             mock_query.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
                {"egg_id": "TEST-BIN-E1", "bin_id": "TEST-BIN", "current_stage": "S1", "status": "Active", "is_deleted": False}
            ]
             mock_query.select.return_value.eq.return_value.execute.return_value.data = [
                {"egg_id": "TEST-BIN-E1", "bin_id": "TEST-BIN"}
            ]
             mock_query.select.return_value.in_.return_value.execute.return_value.data = []
        elif table_name == "bin_observation":
            mock_query.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": "test-session"} 
            ]
        elif table_name == "egg_observation":
             mock_query.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        table_mocks[table_name] = mock_query
        return mock_query

    mock_supabase.table.side_effect = mock_table

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "test-user"
        at.session_state.session_id = "test-session"
        at.session_state.observer_name = "Test Observer"
        at.session_state.workbench_bins = {"TEST-BIN"}
        at.session_state.env_gate_synced = {"TEST-BIN": True}
        at.run(timeout=15)
        
        # Select the egg
        egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
        assert egg_cb is not None, f"Could not find egg checkbox. Labels: {[cb.label for cb in at.checkbox]}"
        egg_cb.check().run(timeout=15)
        
        # Set backdate
        backdate = datetime.date(2025, 1, 1)
        bd_input = next((di for di in at.date_input if "Backdating" in di.label), None)
        assert bd_input is not None, "Could not find backdating date input"
        bd_input.set_value(backdate).run(timeout=15)
        
        # Click SAVE
        save_btn = next((b for b in at.button if b.label == "SAVE"), None)
        assert save_btn is not None, "Could not find SAVE button"
        save_btn.click().run(timeout=15)
        
        # Verify fix using the cached mock
        insert_calls = table_mocks["egg_observation"].insert.mock_calls
        payload_found = False
        for call in insert_calls:
            payload = call[1][0]
            if isinstance(payload, list):
                if any(row.get("timestamp") == backdate.isoformat() for row in payload):
                    payload_found = True
                    break
        
        assert payload_found, f"Observation payload DID NOT contain the backdated timestamp {backdate.isoformat()}."
