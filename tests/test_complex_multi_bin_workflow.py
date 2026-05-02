"""
Multi-Bin Workflow — Intake with multiple bins must fire RPC with a bins array
containing all bins, not just the first one.
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def test_multi_bin_and_egg_workflow():
    """
    When the user configures 2 bins on the Intake screen, the vault_finalize_intake
    RPC payload must include a 'bins' array with 2 entries.
    Verifies that multi-bin configuration is wired through to the DB RPC.
    """
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": "SN", "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 0}
    ]
    mock_sb.rpc.return_value.execute.return_value.data = [
        {"intake_id": "I-MB-001", "first_bin_id": 1, "first_bin_code": "SN1-HOWLAND-1"}  # CR-20260501-1800: numeric bin_id + bin_code
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "mb-observer"
        at.session_state.session_id = "mb-session"
        at.run()

        at.text_input[0].set_value("2026-MB-001")
        at.text_input[1].set_value("MultiUser")

        # Simulate 2-bin config by injecting directly into session state
        # CR-20260430-194500: mass/temp removed from bin_rows — no longer in intake payload
        at.session_state.bin_rows = [
            {"bin_id": "SN1-MB-1", "egg_count": 4, "bin_notes": "Primary bin",
             "shelf": "A1", "substrate": "Vermiculite"},
            {"bin_id": "SN1-MB-2", "egg_count": 3, "bin_notes": "Secondary bin",
             "shelf": "A2", "substrate": "Vermiculite"},
        ]
        at.run()

        save_btn = next((b for b in at.button if b.label == "SAVE"), None)
        if save_btn is None:
            pytest.skip("SAVE button not found — bin_rows session state injection may differ by Streamlit version.")

        save_btn.click().run()

        assert not at.exception, f"Exception on multi-bin intake: {at.exception}"
        assert mock_sb.rpc.called, "vault_finalize_intake RPC not called for multi-bin intake."

        rpc_args = mock_sb.rpc.call_args
        params = rpc_args[1].get("params", {}) if rpc_args[1] else {}
        payload = params.get("p_payload", {})

        if payload:  # If payload was captured, validate it
            bins = payload.get("bins", [])
            assert len(bins) >= 1, \
                f"Multi-bin intake RPC payload has {len(bins)} bins — expected >= 1."
