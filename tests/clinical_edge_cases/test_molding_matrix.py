"""
=============================================================================
File:     tests/clinical_edge_cases/test_molding_matrix.py
Suite:    Phase 3.5 — Clinical Edge Cases: Molding Matrix
Coverage: §5.2 Molding status 1-3.
=============================================================================
"""
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from tests.test_state_machine_edges import _build_obs_mock

def test_molding_options_and_persistence():
    """
    Verify that Molding options 0-3 are available and correctly persisted.
    """
    mock_sb, tables = _build_obs_mock()
    
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "mold-observer"
        at.session_state.session_id = "mold-session"
        at.session_state.observer_name = "Mold Specialist"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        # Select egg
        egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
        egg_cb.check().run(timeout=15)

        # Find Molding selectbox
        mold_sel = next((s for s in at.selectbox if "Molding" in (s.label or "")), None)
        assert mold_sel is not None
        assert 3 in mold_sel.options or "3" in [str(o) for o in mold_sel.options]
        
        # Set to Aggressive (3)
        mold_sel.set_value(3).run(timeout=15)
        
        # Click SAVE
        save_btn = next((b for b in at.button if b.label == "SAVE" and "Append" not in (b.help or "")), None)
        save_btn.click().run(timeout=15)

        # Verify egg_observation insert
        insert_calls = tables["egg_observation"].insert.call_args_list
        payload = insert_calls[-1][0][0]
        if isinstance(payload, list): payload = payload[0]
        assert payload.get("molding") == 3, f"Expected molding=3, got {payload.get('molding')}"
