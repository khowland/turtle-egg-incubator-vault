import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

def test_soft_delete_compliance():
    """
    ADV-16: Verify that clinical data is never hard-deleted (§4).
    """
    mock_supabase = MagicMock()
    table_mocks = {}
    
    def mock_table(table_name):
        if table_name in table_mocks: return table_mocks[table_name]
        m = MagicMock()
        if table_name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [{"bin_id": "B1"}]
        elif table_name == "egg":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
                 {"egg_id": "B1-E1", "bin_id": "B1", "current_stage": "S1", "status": "Active"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [{"egg_id": "B1-E1"}]
        elif table_name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [{"session_id": "admin-session"}]
        
        table_mocks[table_name] = m
        return m

    mock_supabase.table.side_effect = mock_table
    
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        with patch("utils.rbac.can_elevated_clinical_operations", return_value=True):
            at = AppTest.from_file("vault_views/3_Observations.py")
            at.session_state.observer_id = "admin"
            at.session_state.session_id = "admin-session"
            at.session_state.observer_name = "Admin"
            at.session_state.workbench_bins = {"B1"}
            at.session_state.env_gate_synced = {"B1": True}
            at.run(timeout=15)
            
            # Enable Surgical Mode toggle
            surg_toggle = next(t for t in at.toggle if "Surgical" in t.label)
            surg_toggle.set_value(True).run(timeout=15)
            
            # Select egg
            egg_cb = next(cb for cb in at.checkbox if "1" in cb.label)
            egg_cb.check().run(timeout=15)
            
            # The code should now show historical observations
            # We mock the historical observations for the selected egg
            table_mocks["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
                 {"egg_observation_id": "OBS-1", "timestamp": "2026-01-01T00:00:00Z", "stage_at_observation": "S1"}
            ]
            at.run(timeout=15)
            
            # Trigger 'Void' button
            void_btn = next(b for b in at.button if b.label == "Void")
            void_btn.click().run(timeout=15)
            
            # Assert update is used
            update_calls = table_mocks["egg_observation"].update.mock_calls
            assert any("is_deleted': True" in str(call) for call in update_calls), "Surgical void did not set is_deleted=True"
            
            delete_calls = table_mocks["egg_observation"].delete.mock_calls
            assert len(delete_calls) == 0, "Security Violation: Hard delete called on clinical records!"
