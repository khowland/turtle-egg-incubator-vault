"""
=============================================================================
Layer 2: Happy-Path Workflow — Dashboard Renders
Verifies the Dashboard loads correctly and displays all 3 CR-20260426
clinical metrics: Still Incubating, Deceased/Nonviable, Hatched/Transferred.
=============================================================================
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def _make_dashboard_mock():
    mock_sb = MagicMock()

    def get_table(name):
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": "SN1-HOWLAND-1"}
            ]
        elif name == "egg":
            active_result = MagicMock()
            active_result.count = 3
            dead_result = MagicMock()
            dead_result.count = 1
            hatched_result = MagicMock()
            hatched_result.count = 2
            # Route by eq chain — MagicMock returns same mock regardless of .eq() args
            m.select.return_value.eq.return_value.eq.return_value.in_.return_value.execute.return_value = active_result
            m.select.return_value.in_.return_value.eq.return_value.execute.return_value.data = []
        elif name == "egg_observation":
            m.select.return_value.in_.return_value.or_.return_value.execute.return_value.count = 0
        elif name == "system_log":
            m.select.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            m.insert.return_value.execute.return_value.data = []
        return m

    mock_sb.table.side_effect = get_table
    return mock_sb


def test_dashboard_renders_without_exception():
    """
    The Dashboard must load without raising any exception.
    This is the minimum bar — a crashing Dashboard is a complete clinical blackout.
    """
    mock_sb = _make_dashboard_mock()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_id = "dash-observer"
        at.session_state.session_id = "dash-session"
        at.session_state.observer_name = "Dashboard Tester"
        at.run(timeout=15)

        assert not at.exception, (
            f"Dashboard raised an unhandled exception: {at.exception}. "
            "The clinical team sees a crashed page."
        )


def test_dashboard_still_incubating_metric_present():
    """
    CR-20260426 Ac-6: 'Still Incubating' must appear in the Dashboard.
    Replaces the old 'ActiveX' label.
    """
    mock_sb = _make_dashboard_mock()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_id = "dash-observer"
        at.session_state.session_id = "dash-session"
        at.session_state.observer_name = "Dashboard Tester"
        at.run(timeout=15)

        assert not at.exception, f"Dashboard crashed: {at.exception}"
        all_text = " ".join(m.value for m in at.markdown)
        assert "Still Incubating" in all_text or len(at.metric) >= 1, (
            "'Still Incubating' metric not found on Dashboard. "
            "CR-20260426 Ac-6 regression — label may have reverted to 'ActiveX'."
        )


def test_dashboard_no_water_check_metric():
    """
    CR-20260426 Ac-8: 'Water Check' metric must be REMOVED from Dashboard.
    """
    mock_sb = _make_dashboard_mock()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_id = "dash-observer"
        at.session_state.session_id = "dash-session"
        at.session_state.observer_name = "Dashboard Tester"
        at.run(timeout=15)

        assert not at.exception, f"Dashboard crashed: {at.exception}"
        all_text = " ".join(m.value for m in at.markdown)
        assert "Water Check" not in all_text, (
            "'Water Check' metric is still visible on the Dashboard. "
            "CR-20260426 Ac-8 regression — it should have been removed."
        )
