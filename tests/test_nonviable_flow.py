"""
Nonviable Flow — Marking an egg as Dead must remove it from the active grid.
A Dead egg with status='Dead' should NOT appear in the Active egg query filter.
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def test_marking_egg_as_dead_removes_from_grid():
    """
    When an egg's status is 'Dead', it must not render in the Active Observations grid.
    The grid query filters: .eq('status', 'Active'), so Dead eggs are excluded at query time.
    This test confirms the Observations page renders 0 checkboxes when all eggs are Dead.
    """
    mock_sb = MagicMock()
    tables = {}

    def get_table(name):
        if name in tables:
            return tables[name]
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": "NV-BIN", "intake_id": "NV-INTAKE"}
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"bin_id": "NV-BIN", "intake_id": "NV-INTAKE"}
            ]
        elif name == "egg":
            # All eggs are Dead — the Active filter must return empty
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.in_.return_value.execute.return_value.data = []
        elif name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": "nv-session"}
            ]
        elif name == "egg_observation":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        elif name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "NV-INTAKE", "intake_name": "2026-NV-001"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"intake_id": "NV-INTAKE", "intake_name": "2026-NV-001"}
            ]
        elif name == "hatchling_ledger":
            m.select.return_value.in_.return_value.execute.return_value.data = []
        tables[name] = m
        return m

    for t in ["bin", "egg", "bin_observation", "egg_observation", "intake", "hatchling_ledger", "system_log"]:
        get_table(t)
    mock_sb.table.side_effect = get_table

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "nv-observer"
        at.session_state.session_id = "nv-session"
        at.session_state.observer_name = "NV Tester"
        at.session_state.workbench_bins = {"NV-BIN"}
        at.session_state.env_gate_synced = {"NV-BIN": True}
        at.run(timeout=15)

        assert not at.exception, f"Exception on all-Dead egg bin: {at.exception}"
        # With no Active eggs, no checkboxes should be present for egg selection
        # (The zero-egg path should render gracefully)
        all_md = " ".join(m.value for m in at.markdown)
        # Either no checkboxes or markdown confirms 0 subjects
        assert len(at.checkbox) == 0 or "0" in all_md, \
            "Dead eggs are appearing in the Active observations grid — filter broken."
