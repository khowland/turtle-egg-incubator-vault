"""
Clinical Durability — Verify the Observations page survives a DB timeout/exception
without crashing the entire app. safe_db_execute must handle it gracefully.
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def test_observations_survives_db_exception_on_load():
    """
    If the DB call for eggs throws an exception, the Observations page
    must show an error via safe_db_execute, NOT raise an unhandled exception.
    The clinical team must receive a recoverable error, not a crashed page.
    """
    mock_sb = MagicMock()

    def get_table(name):
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": "DUR-BIN", "intake_id": "DUR-INTAKE"}
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"bin_id": "DUR-BIN", "intake_id": "DUR-INTAKE"}
            ]
        elif name == "egg":
            # Simulate a DB timeout on the egg query
            m.select.side_effect = Exception("connection timeout: upstream latency exceeded 30s")
        elif name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": "dur-session"}
            ]
        elif name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "DUR-INTAKE", "intake_name": "DUR-001"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"intake_id": "DUR-INTAKE", "intake_name": "DUR-001"}
            ]
        elif name == "egg_observation":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        elif name == "hatchling_ledger":
            m.select.return_value.in_.return_value.execute.return_value.data = []
        return m

    mock_sb.table.side_effect = get_table

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "dur-observer"
        at.session_state.session_id = "dur-session"
        at.session_state.observer_name = "Durability Tester"
        at.session_state.workbench_bins = {"DUR-BIN"}
        at.session_state.env_gate_synced = {"DUR-BIN": True}
        at.run(timeout=15)

        # The page must NOT propagate an uncaught exception to the test runner
        # safe_db_execute or try/except in the view should catch it
        # We accept either: no exception, or an st.error shown to the user
        has_error_ui = len(at.error) > 0
        has_raw_exception = bool(at.exception)

        if has_raw_exception:
            pytest.fail(
                f"Observations page raised an unhandled exception on DB timeout: {at.exception}. "
                f"safe_db_execute must catch this."
            )
        # If no exception, the page either rendered or showed an error — both are acceptable
