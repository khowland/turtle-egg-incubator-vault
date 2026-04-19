import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import datetime
from tests.mock_utils import build_table_aware_mock

@pytest.fixture
def mock_db():
    table_data = {
        "intake": [{"intake_id": "I-EXISTING-001", "intake_name": "CASE-2026-001"}],
        "bin": [{"bin_id": "BIN-1", "intake_id": "I-EXISTING-001", "is_deleted": False}],
        "egg": [{"egg_id": "BIN-1-E1", "bin_id": "BIN-1", "status": "Active", "current_stage": "S1", "is_deleted": False}],
        "species": [{"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle"}]
    }
    return build_table_aware_mock(table_data)

def test_multi_bin_and_egg_workflow(mock_db):
    """
    Test adding a 2nd bin, adding eggs, and making multi-egg observations.
    """
    db, tables = mock_db
    
    with patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("utils.bootstrap.bootstrap_page", return_value=db), \
         patch("utils.bootstrap.get_supabase", return_value=db):
        
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "test-biologist-uuid"
        at.session_state.session_id = "test-session-uuid"
        at.session_state.workbench_bins = {"BIN-1"}
        at.run()

        # 1. ADD 2ND BIN
        at.selectbox(key="sup_m").set_value("CASE-2026-001")
        ti_bin = next(t for t in at.text_input if t.label == "New Bin ID")
        ti_bin.set_value("BIN-2")
        
        add_bin_btn = next(b for b in at.button if b.label == "ADD")
        add_bin_btn.click().run()
        
        # Verify BIN-2 was inserted
        assert any(call[0][0]["bin_id"] == "BIN-2" for call in tables["bin"].insert.call_args_list)
        
        # Update mock to include BIN-2
        tables["bin"].execute.return_value.data.append({"bin_id": "BIN-2", "intake_id": "I-EXISTING-001", "is_deleted": False})
        at.run()
        
        # 2. ADD EGGS TO BIN-2
        at.selectbox(key="sup_b").set_value("BIN-2").run()
        at.number_input(key="wt_gate").set_value(500.0)
        save_wt_btn = next(b for b in at.button if b.label == "SAVE" and "weights" in (b.help or ""))
        save_wt_btn.click().run() 
        
        ni_mass = next(n for n in at.number_input if "Post-Append Mass" in n.label)
        ni_mass.set_value(600.0)
        ni_eggs = next(n for n in at.number_input if n.label == "Eggs to Add")
        ni_eggs.set_value(5) 
        save_eggs_btn = next(b for b in at.button if b.label == "SAVE" and "Append" in (b.help or ""))
        save_eggs_btn.click().run() 
        
        # 3. MULTI-EGG OBSERVATIONS
        bin2_eggs = [
            {"egg_id": f"BIN-2-E{i}", "bin_id": "BIN-2", "status": "Active", "current_stage": "S1", "is_deleted": False}
            for i in range(1, 6)
        ]
        tables["egg"].execute.return_value.data = bin2_eggs
        
        bin_focus_sel = at.selectbox(key="Current Bin Focus")
        bin2_opt = next(o for o in bin_focus_sel.options if "BIN-2" in o)
        bin_focus_sel.set_value(bin2_opt).run()
        
        # Use more resilient checkbox check - avoid chain calls that might trigger intermediate reruns
        for i in [1, 2]:
            cb = next(c for c in at.checkbox if str(i) in c.label)
            cb.check()
        at.run()
        
        sb_stage = next(s for s in at.selectbox if "Stage" in (s.label or ""))
        sb_stage.set_value("S2")
        # Run after setting selectbox to stabilize the renders
        at.run()
        
        # Find ONLY the property matrix SAVE button
        save_obs_btn = next(b for b in at.button if b.label == "SAVE" and not b.help)
        save_obs_btn.click().run() 
        
        assert len(tables["egg_observation"].insert.call_args_list) > 0
