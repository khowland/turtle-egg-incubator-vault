"""
Bin Retirement Gate — bins with active eggs must NOT be retirable.
Dashboard should only offer retirement for bins where active egg count == 0.
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def _make_dashboard_mock(active_egg_count=0, bin_ids=None):
    """Build a mock that returns a specified number of active eggs for the bin."""
    bin_ids = bin_ids or ["TEST-BIN-1"]
    mock_sb = MagicMock()
    tables = {}

    def get_table(name):
        if name in tables:
            return tables[name]
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": bid} for bid in bin_ids
            ]
        elif name == "egg":
            # Count query: returns active_egg_count items per bin
            m.select.return_value.in_.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": bin_ids[0]} for _ in range(active_egg_count)
            ]
            # Dead/heatmap query
            m.select.return_value.eq.return_value.eq.return_value.in_.return_value.execute.return_value.data = []
            # Count attributes used by the KPI fetch (count="exact")
            mock_count = MagicMock()
            mock_count.count = active_egg_count
            m.select.return_value.eq.return_value.eq.return_value.in_.return_value.execute.return_value = mock_count
        elif name == "egg_observation":
            m.select.return_value.in_.return_value.or_.return_value.execute.return_value.count = 0
        elif name == "system_log":
            m.select.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            m.insert.return_value.execute.return_value.data = []
        tables[name] = m
        return m

    for t in ["bin", "egg", "egg_observation", "system_log"]:
        get_table(t)

    mock_sb.table.side_effect = get_table
    return mock_sb


def test_bin_with_active_eggs_not_offered_for_retirement():
    """
    A bin with >=1 active eggs must NOT appear in the retirement selectbox.
    The dashboard only retires bins where active egg count == 0.
    """
    mock_sb = _make_dashboard_mock(active_egg_count=3)

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_id = "gate-obs"
        at.session_state.session_id = "gate-ses"
        at.session_state.observer_name = "Gate Tester"
        at.run(timeout=15)

        assert not at.exception, f"Dashboard crashed: {at.exception}"
        # Retirement section header should NOT appear when all bins have active eggs
        all_md = " ".join(m.value for m in at.markdown)
        # The retirement subheader only renders when retirement_targets_list is non-empty
        # With active eggs, the bin should NOT be in the targets list
        assert "Remove Empty Bins" not in all_md, \
            "Bin with active eggs incorrectly offered for retirement."


def test_bin_with_zero_eggs_offered_for_retirement():
    """
    A bin with 0 active eggs MUST appear in the retirement selectbox.
    """
    mock_sb = _make_dashboard_mock(active_egg_count=0)

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)):
        at = AppTest.from_file("vault_views/1_Dashboard.py")
        at.session_state.observer_id = "gate-obs"
        at.session_state.session_id = "gate-ses"
        at.session_state.observer_name = "Gate Tester"
        at.run(timeout=15)

        assert not at.exception, f"Dashboard crashed on empty bin: {at.exception}"
        # With 0 active eggs the bin qualifies — the retirement UI must appear
        all_md = " ".join(m.value for m in at.markdown)
        has_retirement_ui = "Remove Empty Bins" in all_md or len(at.selectbox) > 0
        assert has_retirement_ui, \
            "Empty bin (0 active eggs) was not offered for retirement — UI gate broken."
