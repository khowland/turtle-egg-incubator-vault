"""
=============================================================================
File:     tests/test_mid_season_intake.py
Suite:    Phase 3.5 — Clinical Workflow: Mid-Season Intake
Coverage: §1.5 Supplemental Bin, §1.6 Supplemental Eggs.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from tests.test_state_machine_edges import _build_obs_mock

def test_add_eggs_to_existing_bin():
    """
    Verify the sidebar workflow for adding eggs to an existing bin mid-season.
    """
    mock_sb, tables = _build_obs_mock()
    # Intake records for the supplemental bin sidebar
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"intake_id": "MID-CASE", "intake_name": "CASE-MID-001", "is_deleted": False}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "mid-observer"
        at.session_state.session_id = "mid-session"
        at.session_state.observer_name = "Mid Biologist"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)
        
        expander = next((e for e in at.sidebar.expander if "Add Eggs to Existing Bin" in e.label), None)
        assert expander is not None
        
        eggs_ni = next((n for n in expander.number_input if "Eggs to Add" in (n.label or "")), None)
        eggs_ni.set_value(5)
        
        weight_ni = next((n for n in expander.number_input if "Mass" in (n.label or "")), None)
        weight_ni.set_value(150.5)
        
        save_btn = next((b for b in expander.button if b.label == "SAVE"), None)
        save_btn.click().run(timeout=15)
        
        assert tables["egg"].insert.called, "Supplemental eggs were not inserted."
        assert tables["bin_observation"].insert.called, "Bin weight not updated."

def test_add_new_bin_to_existing_case():
    """
    Verify the sidebar workflow for adding a new bin to an existing intake case.
    """
    mock_sb, tables = _build_obs_mock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"intake_id": "MID-CASE", "intake_name": "CASE-MID-001"}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "mid-observer"
        at.session_state.session_id = "mid-session"
        at.session_state.observer_name = "Mid Biologist"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)
        
        expander = next((e for e in at.sidebar.expander if "Add a Bin to a Case" in e.label), None)
        assert expander is not None
        
        bin_id_input = next((ti for ti in expander.text_input if "Bin ID" in (ti.label or "")), None)
        bin_id_input.set_value("NEW-BIN-MID")
        
        add_btn = next((b for b in expander.button if b.label == "ADD"), None)
        add_btn.click().run(timeout=15)
        
        assert tables["bin"].insert.called, "New bin not inserted."
