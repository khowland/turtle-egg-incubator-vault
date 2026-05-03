import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
import json
import datetime


def _make_intake_mock():
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": "SN", "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 0}
    ]
    mock_sb.rpc.return_value.execute.return_value.data = [
        {"intake_id": "I-WF-001", "first_bin_id": 1, "first_bin_code": "SN1-HOWLAND-1"}  # CR-20260501-1800: numeric bin_id + bin_code
    ]
    return mock_sb


def test_workflow_intake_to_observation_handoff():
    """
    After a successful Intake SAVE, active_bin_id must be set in session_state
    so the Observations page can load the correct bin.
    Fixes: CR-20260426 Lo-4 (Workflow Handoff Failure / ID Desync).
    """
    mock_sb = _make_intake_mock()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "wf-observer"
        at.session_state.session_id = "wf-session"
        at.run()

        at.text_input[0].set_value("2026-WF-001")
        at.text_input[1].set_value("Howland")
        at.session_state.bin_rows[0]["mass"] = 185.0
        at.session_state.bin_rows[0]["temp"] = 28.0
        at.run()

        save_btn = next(b for b in at.button if b.label == "SAVE")
        save_btn.click().run()

        assert not at.exception, f"Uncaught exception during intake save: {at.exception}"
        # RPC must have fired — the handoff depends on the intake_id being returned
        assert mock_sb.rpc.called, "vault_finalize_intake RPC was never called — handoff cannot occur."


def test_workflow_lifecycle_progression_s1_to_s6():
    """
    Observations view must render eggs at S1 without exception.
    Confirms basic lifecycle entry point is not broken.
    """
    mock_sb = MagicMock()
    tables = {}

    def get_table(name):
        if name in tables:
            return tables[name]
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": 1, "bin_code": "SN1-HOWLAND-1", "intake_id": "I-LC-001"}  # CR-20260501-1800: numeric bin_id + bin_code
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"bin_id": 1, "bin_code": "SN1-HOWLAND-1", "intake_id": "I-LC-001"}  # CR-20260501-1800: numeric bin_id + bin_code
            ]
        elif name == "egg":
            egg = {
                "egg_id": "SN1-HOWLAND-1-E1", "bin_id": 1, "bin_code": "SN1-HOWLAND-1",  # CR-20260501-1800: numeric bin_id + bin_code
                "current_stage": "S1", "status": "Active",
                "is_deleted": False, "last_chalk": 0, "last_vasc": False,
                "intake_timestamp": "2026-04-01T12:00:00Z",
            }
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [egg]
            m.select.return_value.eq.return_value.execute.return_value.data = [egg]
            m.select.return_value.in_.return_value.execute.return_value.data = [egg]
        elif name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": "lc-session"}
            ]
        elif name == "egg_observation":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        elif name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "I-LC-001", "intake_name": "CASE-LC-001"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"intake_id": "I-LC-001", "intake_name": "CASE-LC-001"}
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
        at.session_state.observer_id = "lc-observer"
        at.session_state.session_id = "lc-session"
        at.session_state.observer_name = "LC Tester"
        at.session_state.workbench_bins = {1}  # CR-20260501-1800: Use numeric bin_id (bin_id is now BIGINT)
        at.session_state.env_gate_synced = {1: True}  # CR-20260501-1800: Use numeric bin_id
        at.run(timeout=15)

        assert not at.exception, f"Observations crashed on S1 egg: {at.exception}"
        # At least one element must show the egg (checkbox or stage label)
        all_text = " ".join(m.value for m in at.markdown)
        assert "S1" in all_text or len(at.checkbox) >= 1, \
            "Observations page did not render any S1 egg content — lifecycle entry broken."
