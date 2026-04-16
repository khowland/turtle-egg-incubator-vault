import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import json
import datetime

class SupabaseMockFactory:
    def __init__(self):
        self.mock_client = MagicMock()
        self.responses = {}
        self.mock_client.table.side_effect = self.get_table_mock
        self.rpc_response = None
        self.mock_client.rpc.side_effect = self.get_rpc_mock

    def set_response(self, table, data):
        self.responses[table] = data

    def get_table_mock(self, table_name):
        mock_obj = MagicMock()
        data = self.responses.get(table_name, [])
        # We need to make the chain very resilient
        mock_obj.select.return_value.execute.return_value.data = data
        mock_obj.select.return_value.eq.return_value.execute.return_value.data = data
        mock_obj.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = data
        mock_obj.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = data
        mock_obj.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = data
        mock_obj.select.return_value.order.return_value.limit.return_value.execute.return_value.data = data
        return mock_obj

    def get_rpc_mock(self, name, params=None):
        mock_rpc = MagicMock()
        mock_rpc.execute.return_value.data = self.rpc_response
        return mock_rpc

@pytest.fixture
def mock_factory():
    return SupabaseMockFactory()

def test_workflow_intake_to_observation_handoff(mock_factory):
    """
    W-1: Verify that eggs created in Intake appear in Observations workbench.
    """
    factory = mock_factory
    factory.set_response("species", [{"species_id": "SN", "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}])
    factory.rpc_response = [{"intake_id": "I-HANDOFF-1", "first_bin_id": "BIN-A1"}]
    
    with patch("utils.bootstrap.bootstrap_page", return_value=factory.mock_client):
        at_intake = AppTest.from_file("vault_views/2_New_Intake.py")
        at_intake.session_state.observer_id = "biologist-1"
        at_intake.session_state.session_id = "sess-123"
        at_intake.run()
        
        at_intake.text_input[0].set_value("CASE-HANDOFF")
        at_intake.run()
        
        save_button = next(b for b in at_intake.button if b.label == "SAVE")
        save_button.click().run()
        
        # Verify active_case_id in session state
        # In at.session_state, we check if it is set.
        assert at_intake.session_state.get("active_case_id") == "I-HANDOFF-1"

def test_workflow_lifecycle_progression_s1_to_s6(mock_factory):
    """
    W-4: Verify egg progression from S1 to S6 and Hatchling Ledger creation.
    """
    factory = mock_factory
    factory.set_response("bin_observation", [{"session_id": "sess-lifecycle"}]) # Bypass hydration gate
    factory.set_response("bin", [{"bin_id": "BIN-L1", "intake_id": "I-LIFE-1"}])
    factory.set_response("egg", [{"egg_id": "BIN-L1-E1", "current_stage": "S1", "status": "Active", "bin_id": "BIN-L1", "intake_timestamp": "2026-01-01T12:00:00Z"}])
    factory.set_response("intake", [{"intake_id": "I-LIFE-1", "intake_name": "CASE-L"}])
    factory.set_response("egg_observation", [])
    
    with patch("utils.bootstrap.bootstrap_page", return_value=factory.mock_client):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.session_id = "sess-lifecycle"
        at.session_state.observer_id = "biologist-uuid"
        at.session_state.workbench_bins = {"BIN-L1"}
        at.run()
        
        # Check for error markdown (diagnostics)
        if at.exception:
            raise at.exception[0]
            
        # Select the egg checkbox
        # In 3_Observations.py, the checkbox label is the egg ID number.
        checkbox = next(c for c in at.checkbox if "1" in c.label) # E1
        checkbox.check().run()
        
        # Change stage to S6 (Hatched)
        stage_select = next(s for s in at.selectbox if "Stage" in s.label)
        stage_select.set_value("S6").run()
        
        # Submit Observation
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Verify hatchling_ledger insert was called
        insert_calls = [call for call in factory.mock_client.table.call_args_list if call[0][0] == "hatchling_ledger"]
        assert len(insert_calls) > 0
