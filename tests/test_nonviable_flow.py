"""
=============================================================================
File:     tests/test_nonviable_flow.py
Suite:    Phase 3.5 — Clinical Workflow: Non-Viable Eggs
Coverage: §1.4 REMOVE vocabulary, status='Dead' lifecycle transition.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from tests.mock_utils import build_table_aware_mock

def test_marking_egg_as_dead_removes_from_grid():
    """
    Test that marking an egg as 'Dead' updates its status and removes it from
    the active observation grid on rerun.
    """
    table_data = {
        "bin": [{"bin_id": "SM-BIN", "intake_id": "SM-CASE"}],
        "egg": [{"egg_id": "SM-BIN-E1", "bin_id": "SM-BIN", "status": "Active", "current_stage": "S1", "is_deleted": False}],
        "bin_observation": [{"session_id": "dead-session"}],
        "egg_observation": []
    }
    mock_sb, tables = build_table_aware_mock(table_data)
    
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "dead-observer"
        at.session_state.session_id = "dead-session"
        at.session_state.observer_name = "Clinic Staff"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        # Select egg
        egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
        assert egg_cb is not None
        egg_cb.check().run(timeout=15)

        # Find Status selectbox and select Dead
        status_sel = next((s for s in at.selectbox if "Status" in (s.label or "")), None)
        assert status_sel is not None
        status_sel.select("Dead").run(timeout=15)
        
        # BEFORE clicking SAVE, update the mock to reflect that the egg will be Dead in the next grid fetch
        tables["egg"].select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        
        # Click SAVE
        save_btn = next((b for b in at.button if b.label == "SAVE" and "Append" not in (b.help or "")), None)
        assert save_btn is not None
        save_btn.click().run(timeout=15)

        # Verify egg table update was called with Dead
        egg_updates = tables["egg"].update.call_args_list
        assert len(egg_updates) > 0, "egg.update was not called."
        payload = egg_updates[-1][0][0]
        assert payload.get("status") == "Dead", f"Expected status='Dead', got {payload.get('status')}"
        
        # Verify it's gone from grid
        cbs = [cb.label for cb in at.checkbox if "**1**" in cb.label]
        assert len(cbs) == 0, f"Egg still visible in grid after being marked Dead. Found: {cbs}"

