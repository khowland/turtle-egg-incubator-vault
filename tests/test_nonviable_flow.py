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
from tests.test_state_machine_edges import _build_obs_mock

def test_marking_egg_as_dead_removes_from_grid():
    """
    Test that marking an egg as 'Dead' updates its status and removes it from
    the active observation grid on rerun.
    """
    mock_sb, tables = _build_obs_mock()
    
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

        # Find Status selectbox
        status_sel = next((s for s in at.selectbox if "Status" in (s.label or "")), None)
        assert status_sel is not None, "Status selectbox not found in Property Matrix."
        
        # Update mock AFTER st.run() to ensure it applies to the NEXT render
        # History includes a deleted observation
        tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
            {"egg_observation_id": "OBS-DELETED", "egg_id": "E-99", "timestamp": "2026-01-01T10:00:00Z", "stage_at_observation": "S1", "observer_id": "bio-1", "void_reason": "test-void", "is_deleted": True}
        ]
        
        # Click SAVE
        save_btn = next((b for b in at.button if b.label == "SAVE" and "Append" not in (b.help or "")), None)
        assert save_btn is not None
        save_btn.click().run(timeout=15)

        # Verify egg table update
        egg_updates = tables["egg"].update.call_args_list
        assert len(egg_updates) > 0, "egg.update was not called."
        payload = egg_updates[-1][0][0]
        # The test might still see 'Active' if the click().run() uses the initial state.
        # We check the database update itself for correctness.
        assert payload.get("status") == "Dead", f"Expected status='Dead', got {payload.get('status')}"
        
        # Verify it's gone from grid
        cbs = [cb.label for cb in at.checkbox if cb.label == "**1**"]
        assert len(cbs) == 0, f"Egg still visible in grid after being marked Dead. Found: {cbs}"
