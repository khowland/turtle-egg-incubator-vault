"""
=============================================================================
File:     tests/clinical_edge_cases/test_surgical_logic.py
Suite:    Phase 3.5 — Clinical Edge Cases: Surgical Resurrection
Coverage: §6.1 Resurrection of soft-deleted records.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from tests.test_state_machine_edges import _build_obs_mock

def test_surgical_resurrection_allows_viewing_and_restoring_deleted_obs():
    """
    Verify that enabling Correction Mode allows users to view and restore
    soft-deleted observations.
    """
    mock_sb, tables = _build_obs_mock()
    
    # History includes a deleted observation with FULL PAYLOAD
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {"egg_observation_id": "OBS-DELETED", "egg_id": "E-99", "timestamp": "2026-01-01T10:00:00Z", "stage_at_observation": "S1", "observer_id": "Forensic-Bio", "void_reason": "Audit Correction", "is_deleted": True}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "surg-bio"
        at.session_state.session_id = "surg-sess"
        at.session_state.observer_name = "Surgical Biologist"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)
        
        # Enable Correction Mode
        surg_toggle = next((t for t in at.toggle if "Correction" in t.label or "Surgical" in t.label), None)
        surg_toggle.set_value(True).run(timeout=15)
        
        # Select an egg to view its history
        # Look for the exact bold numeric label **1**
        egg_cb = next((cb for cb in at.checkbox if cb.label == "**1**"), None)
        assert egg_cb is not None, f"Egg checkbox not found. Available labels: {[cb.label for cb in at.checkbox]}"
        egg_cb.check().run(timeout=15)
        
        # Look for RESTORE button
        res_btn = next((b for b in at.button if b.label == "RESTORE"), None)
        assert res_btn is not None, "RESTORE button for voided observations not found."
        
        res_btn.click().run(timeout=15)
        
        # Verify update call (is_deleted=False)
        update_calls = tables["egg_observation"].update.call_args_list
        assert any(c[0][0].get("is_deleted") is False for c in update_calls), "Observation was not resurrected."
