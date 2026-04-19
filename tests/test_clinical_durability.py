import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

from tests.mock_utils import build_table_aware_mock

def test_soft_delete_compliance():
    """
    ADV-16: Verify that clinical data is never hard-deleted (§4).
    """
    table_data = {
        "bin": [{"bin_id": "B1"}],
        "egg": [{"egg_id": "B1-E1", "bin_id": "B1", "current_stage": "S1", "status": "Active"}],
        "bin_observation": [{"session_id": "admin-session"}],
        "egg_observation": [{"egg_observation_id": "OBS-1", "timestamp": "2026-01-01T00:00:00Z", "stage_at_observation": "S1"}]
    }
    mock_supabase, tables = build_table_aware_mock(table_data)
    
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "admin"
        at.session_state.session_id = "admin-session"
        at.session_state.observer_name = "Admin"
        at.session_state.workbench_bins = {"B1"}
        at.session_state.env_gate_synced = {"B1": True}
        at.run(timeout=15)
        
        # Enable Surgical Mode toggle
        surg_toggle = next(t for t in at.toggle if "Surgical" in t.label or "Correction" in t.label)
        surg_toggle.set_value(True).run(timeout=15)
        
        # Select an egg to view its history
        repair_sel = next((s for s in at.selectbox if "Surgery" in (s.label or "")), None)
        assert repair_sel is not None, "Select Egg for Surgery selectbox not found."
        repair_sel.set_value(repair_sel.options[0]).run(timeout=15)
        
        # Trigger 'Void' button (Check both variants)
        void_btn = next((b for b in at.button if b.label == "Void" or b.label == "REMOVE"), None)
        assert void_btn is not None, "Void/REMOVE button not found."
        void_btn.click().run(timeout=15)
        
        # Assert update is used
        update_calls = tables["egg_observation"].update.mock_calls
        assert any("'is_deleted': True" in str(call) for call in update_calls), "Surgical void did not set is_deleted=True"
        
        delete_calls = tables["egg_observation"].delete.mock_calls
        assert len(delete_calls) == 0, "Security Violation: Hard delete called on clinical records!"

