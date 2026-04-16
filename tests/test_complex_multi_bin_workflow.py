import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import datetime

class SupabaseMock:
    def __init__(self):
        self.table_clients = {}
        self.rpc_mock = MagicMock()
        
    def table(self, name):
        if name not in self.table_clients:
            mock = MagicMock()
            mock.select.return_value = mock
            mock.insert.return_value = mock
            mock.update.return_value = mock
            mock.delete.return_value = mock
            mock.eq.return_value = mock
            mock.in_.return_value = mock
            mock.order.return_value = mock
            mock.limit.return_value = mock
            
            # Setup specific data returns
            data_container = MagicMock()
            data_container.data = []
            data_container.count = 0
            mock.execute.return_value = data_container
            
            self.table_clients[name] = mock
        return self.table_clients[name]

    def rpc(self, name, params=None):
        return self.rpc_mock(name, params)

@pytest.fixture
def mock_db():
    return SupabaseMock()

def test_multi_bin_and_egg_workflow(mock_db):
    """
    Test adding a 2nd bin to an existing intake, adding eggs, and making multi-egg observations.
    """
    db = mock_db
    
    # 1. SETUP: Existing Intake and Bin 1
    db.table("intake").execute.return_value.data = [
        {"intake_id": "I-EXISTING-001", "intake_name": "CASE-2026-001"}
    ]
    db.table("bin").execute.return_value.data = [
        {"bin_id": "BIN-1", "intake_id": "I-EXISTING-001", "is_deleted": False}
    ]
    db.table("egg").execute.return_value.data = [
        {"egg_id": "BIN-1-E1", "bin_id": "BIN-1", "status": "Active", "current_stage": "S1", "is_deleted": False},
        {"egg_id": "BIN-1-E2", "bin_id": "BIN-1", "status": "Active", "current_stage": "S1", "is_deleted": False}
    ]
    
    # Bypass RBAC for simplicity in test
    with patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("utils.bootstrap.bootstrap_page", return_value=db), \
         patch("utils.bootstrap.get_supabase", return_value=db):
        
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "test-biologist-uuid"
        at.session_state.session_id = "test-session-uuid"
        at.session_state.workbench_bins = {"BIN-1"}
        at.run()
        
        if at.exception:
            raise at.exception[0]

        # 2. ADD 2ND BIN
        at.selectbox(key="sup_m").set_value("CASE-2026-001")
        ti_bin = next(t for t in at.text_input if t.label == "New Bin ID")
        ti_bin.set_value("BIN-2")
        
        # Click the ADD button for supplemental bin
        add_bin_btn = next(b for b in at.button if b.label == "ADD")
        add_bin_btn.click().run()
        
        # Verify BIN-2 was inserted
        insert_calls = [call for call in db.table("bin").insert.call_args_list]
        assert any(call[0][0]["bin_id"] == "BIN-2" for call in insert_calls)
        assert "BIN-2" in at.session_state.workbench_bins
        
        # 3. ADD EGGS TO BIN-2
        # Mock that BIN-2 now exists in the next run
        db.table("bin").execute.return_value.data.append({"bin_id": "BIN-2", "intake_id": "I-EXISTING-001", "is_deleted": False})
        
        # We need to run again so the selectbox options are rebuilt with BIN-2
        at.run()
        at.selectbox(key="sup_b").set_value("BIN-2").run()
        
        # Weight check for Bin 2
        at.number_input(key="wt_gate").set_value(500.0)
        save_wt_btn = next(b for b in at.button if b.label == "SAVE" and "weights" in b.help)
        save_wt_btn.click().run() 
        
        # Add 5 eggs
        ni_eggs = next(n for n in at.number_input if n.label == "Eggs to Add")
        ni_eggs.set_value(5) 
        save_eggs_btn = next(b for b in at.button if b.label == "SAVE" and "Append" in b.help)
        save_eggs_btn.click().run() 
        
        # Verify 5 eggs were added to BIN-2
        egg_insert_calls = [call for call in db.table("egg").insert.call_args_list]
        last_egg_insert = egg_insert_calls[-1][0][0]
        assert len(last_egg_insert) == 5
        assert last_egg_insert[0]["bin_id"] == "BIN-2"
        
        # 4. MULTI-EGG OBSERVATIONS
        # Mock eggs for BIN-2 (Active eggs for the grid)
        bin2_eggs = [
            {"egg_id": f"BIN-2-E{i}", "bin_id": "BIN-2", "status": "Active", "current_stage": "S1", "is_deleted": False}
            for i in range(1, 6)
        ]
        db.table("egg").execute.return_value.data = bin2_eggs # Switch focus fully for this run
        
        # Select Bin 2 in focus
        at.selectbox(key="Current Bin Focus").set_value("⚪ BIN-2 (0/5)").run()
        
        # Check first 3 eggs in Bin 2
        cb1 = next(c for c in at.checkbox if "E1" in c.label or " 1 " in c.label or c.label.endswith("1"))
        cb2 = next(c for c in at.checkbox if "E2" in c.label or " 2 " in c.label or c.label.endswith("2"))
        cb3 = next(c for c in at.checkbox if "E3" in c.label or " 3 " in c.label or c.label.endswith("3"))
        cb1.check()
        cb2.check()
        cb3.check()
        at.run()
        
        # Set stage to S2
        # Fixed: The selectbox might not have a label if it's the 1st one in the container
        sb_stage = next(s for s in at.selectbox if s.key is None and "Stage" in (s.label or ""))
        sb_stage.set_value("S2")
        
        # Save observation button (primary)
        save_obs_btn = next(b for b in at.button if b.label == "SAVE" and getattr(b, "type", "") == "primary")
        save_obs_btn.click().run() 
        
        # Verify observations were inserted
        obs_insert_calls = [call for call in db.table("egg_observation").insert.call_args_list]
        last_obs_insert = obs_insert_calls[-1][0][0]
        assert len(last_obs_insert) == 3

        print("✅ SUCCESS: Complex multi-bin lifecycle verified.")
