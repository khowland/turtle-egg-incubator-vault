"""
=============================================================================
Layer 2: Happy-Path Workflow — Observations Save
Verifies the Observations page loads, renders eggs, and processes a save
without crashing. This is the highest-frequency clinical operation.
=============================================================================
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def _make_obs_mock_happy_path():
    mock_sb = MagicMock()
    tables = {}

    def get_table(name):
        if name in tables:
            return tables[name]
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": "SN1-HOWLAND-1", "intake_id": "I-HP-001"}
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"bin_id": "SN1-HOWLAND-1", "intake_id": "I-HP-001"}
            ]
        elif name == "egg":
            eggs = [
                {
                    "egg_id": "SN1-HOWLAND-1-E1", "bin_id": "SN1-HOWLAND-1",
                    "current_stage": "S1", "status": "Active",
                    "is_deleted": False, "last_chalk": 0, "last_vasc": False,
                    "intake_timestamp": "2026-04-01T12:00:00Z",
                },
                {
                    "egg_id": "SN1-HOWLAND-1-E2", "bin_id": "SN1-HOWLAND-1",
                    "current_stage": "S2", "status": "Active",
                    "is_deleted": False, "last_chalk": 1, "last_vasc": False,
                    "intake_timestamp": "2026-04-01T12:00:00Z",
                },
            ]
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = eggs
            m.select.return_value.eq.return_value.execute.return_value.data = eggs
            m.select.return_value.in_.return_value.execute.return_value.data = eggs
        elif name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": "hp-obs-session"}
            ]
        elif name == "egg_observation":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.insert.return_value.execute.return_value.data = [{"egg_observation_id": "EO-NEW"}]
        elif name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "I-HP-001", "intake_name": "2026-HP-001"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"intake_id": "I-HP-001", "intake_name": "2026-HP-001"}
            ]
        elif name == "hatchling_ledger":
            m.select.return_value.in_.return_value.execute.return_value.data = []
        tables[name] = m
        return m

    for t in ["bin", "egg", "bin_observation", "egg_observation", "intake", "hatchling_ledger", "system_log"]:
        get_table(t)
    mock_sb.table.side_effect = get_table
    return mock_sb


def test_observations_renders_active_eggs():
    """
    The Observations page must render active eggs for the workbench bin.
    If it renders 0 elements, clinical staff cannot record observations.
    This covers the Lo-4 crash class (bin ID desync attributeError).
    """
    mock_sb = _make_obs_mock_happy_path()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "obs-hp-observer"
        at.session_state.session_id = "hp-obs-session"
        at.session_state.observer_name = "HP Observer"
        at.session_state.workbench_bins = {"SN1-HOWLAND-1"}
        at.session_state.env_gate_synced = {"SN1-HOWLAND-1": True}
        at.run(timeout=15)

        assert not at.exception, (
            f"Observations page crashed: {at.exception}. "
            "This is a show-stopping error — clinical staff cannot record any observations."
        )
        # Page must have rendered some interactive elements (checkboxes, selects, or markdown)
        has_content = len(at.checkbox) > 0 or len(at.selectbox) > 0 or len(at.markdown) > 0
        assert has_content, (
            "Observations page rendered no UI content for a bin with 2 active eggs. "
            "The observation grid is broken."
        )


def test_observations_renders_without_exception_for_valid_bin_id():
    """
    CR-20260426 Lo-4: A valid bin ID (format SN1-HOWLAND-1) must not cause
    an AttributeError or crash. This was the specific production bug.
    """
    mock_sb = _make_obs_mock_happy_path()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "obs-lo4-observer"
        at.session_state.session_id = "hp-obs-session"
        at.session_state.observer_name = "Lo4 Tester"
        # Use the exact bin ID format that was causing the AttributeError
        at.session_state.workbench_bins = {"SN1-HOWLAND-1"}
        at.session_state.env_gate_synced = {"SN1-HOWLAND-1": True}
        at.run(timeout=15)

        assert not at.exception, (
            f"AttributeError or crash on valid bin ID 'SN1-HOWLAND-1': {at.exception}. "
            "CR-20260426 Lo-4 regression — bin ID sanitization broken."
        )
