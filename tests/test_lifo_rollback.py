"""
=============================================================================
File:     tests/test_lifo_rollback.py
Suite:    Phase 3.5 — Clinical Workflow: LIFO Rollback
Coverage: §4.2 LIFO enforcement, state restoration.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from tests.test_state_machine_edges import _build_obs_mock

def test_lifo_gate_prevents_intermediate_void():
    """
    Verify that only the latest observation has an enabled REMOVE button.
    """
    mock_sb, tables = _build_obs_mock()
    
    # Create 2 observations for the same egg with full forensic fields
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {"egg_observation_id": "OBS-LATEST", "egg_id": "SM-BIN-E1", "timestamp": "2026-02-10T10:00:00Z", "stage_at_observation": "S3", "observer_id": "bio", "chalking": 1, "vascularity": True, "molding": 0, "leaking": 0, "void_reason": None, "is_deleted": False},
        {"egg_observation_id": "OBS-OLD", "egg_id": "SM-BIN-E1", "timestamp": "2026-02-01T10:00:00Z", "stage_at_observation": "S2", "observer_id": "bio", "chalking": 1, "vascularity": True, "molding": 0, "leaking": 0, "void_reason": None, "is_deleted": False}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "sm-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "SM Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)
        
        # Enable Correction Mode
        surg_toggle = next((t for t in at.toggle if "Correction" in t.label or "Surgical" in t.label), None)
        surg_toggle.set_value(True)
        at.run(timeout=15)
        
        # Diagnostic
        print(f"DEBUG: Selectboxes: {[s.label for s in at.selectbox]}")
        print(f"DEBUG: Selected Bin: {at.selectbox[0].value if at.selectbox else 'N/A'}")
        print(f"DEBUG: Checkboxes: {[cb.label for cb in at.checkbox]}")
        
        # Select an egg to view its history
        # In Surgical Mode, we use a selectbox
        repair_sel = next((s for s in at.selectbox if "Surgery" in (s.label or "")), None)
        assert repair_sel is not None, "Select Egg for Surgery selectbox not found."
        repair_sel.set_value("🔍 SM-BIN-E1").run(timeout=15)
        
        # Check buttons using keys instead of labels to satisfy §12.5
        btns = [b for b in at.button if b.key and "void_" in b.key]
        assert len(btns) == 2, "Should show 2 REMOVE buttons in timeline."
        
        # The latest one
        latest_btn = next((b for b in btns if "OBS-LATEST" in b.key), None)
        old_btn = next((b for b in btns if "OBS-OLD" in b.key), None)
        
        assert latest_btn is not None and not latest_btn.disabled, "Latest observation should be retirable."
        assert old_btn is not None and old_btn.disabled, "Older observation should have DISABLED REMOVE button (LIFO Gate)."
