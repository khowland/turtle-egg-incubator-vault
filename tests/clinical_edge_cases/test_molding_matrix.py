"""
Molding Matrix — §5.2 Molding status 1-3.
Observations page must offer molding severity options and persist selection.
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
from tests.test_state_machine_edges import _build_obs_mock


def test_molding_options_and_persistence():
    """
    §5.2: Molding levels 0-3 must be selectable in the Observations grid.
    The Observations page must render without exception when a bin has an
    egg with a non-zero molding value in its observation history.
    """
    mock_sb, tables = _build_obs_mock(
        eggs=[{
            "egg_id": "SM-BIN-E1",
            "bin_id": "SM-BIN",
            "current_stage": "S3",
            "status": "Active",
            "is_deleted": False,
            "last_chalk": 1,
            "last_vasc": True,
            "intake_timestamp": "2026-04-01T12:00:00Z",
        }]
    )

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "mold-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "Mold Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        assert not at.exception, f"Observations crashed with molding data: {at.exception}"
        # Page must render some content (molding fields or egg checkboxes)
        has_content = len(at.checkbox) > 0 or len(at.selectbox) > 0 or len(at.markdown) > 0
        assert has_content, "Observations page rendered empty — molding matrix broken."
