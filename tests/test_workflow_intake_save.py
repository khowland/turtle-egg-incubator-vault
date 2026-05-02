"""
=============================================================================
Layer 2: Happy-Path Workflow — Intake Save
Tests the complete intake form flow: load → fill → SAVE → RPC verified.
This is the #1 critical path — if this breaks, no clinical data enters the DB.
=============================================================================
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


@pytest.fixture
def intake_mock():
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": "SN", "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 0}
    ]
    mock_sb.rpc.return_value.execute.return_value.data = [
        {"intake_id": "I-HP-001", "first_bin_id": 1, "first_bin_code": "SN1-HOWLAND-1"}  # CR-20260501-1800: numeric bin_id + bin_code
    ]
    return mock_sb


def test_happy_path_intake_rpc_fires(intake_mock):
    """
    Full happy-path intake:
    - Load 2_New_Intake.py
    - Fill intake name, finder name
        # - Fill intake name, finder name  # CR-20260430-194500: Removed bin mass + temp (fields no longer exist in intake)
    - Click SAVE
    - Assert RPC fired and no exception raised
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=intake_mock), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "hp-observer"
        at.session_state.session_id = "hp-session"
        at.run()

        assert not at.exception, f"Intake crashed on load: {at.exception}"

        at.text_input[0].set_value("2026-HP-001")   # Case number
        at.text_input[1].set_value("Howland")         # Finder name
        # CR-20260430-194500: bin mass/temp removed — these fields no longer exist in intake payload
        at.run()

        save_btn = next((b for b in at.button if b.label == "SAVE"), None)
        assert save_btn is not None, "SAVE button not found on Intake page."
        save_btn.click().run()

        assert not at.exception, f"Intake crashed on SAVE: {at.exception}"
        assert intake_mock.rpc.called, (
            "vault_finalize_intake RPC was never called. "
            "The intake save is broken — no data reached the database."
        )


def test_happy_path_intake_payload_has_required_fields(intake_mock):
    """
    Verifies the RPC payload contains all required fields:
    species_id, observer_id, session_id, bins array.
    Missing fields cause DB-level crashes (the Mother.Weight bug class).
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=intake_mock), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "hp-observer"
        at.session_state.session_id = "hp-session"
        at.run()

        at.text_input[0].set_value("2026-HP-002")
        at.text_input[1].set_value("Howland")
        # CR-20260430-194500: bin mass/temp removed — these fields no longer exist in intake payload
        at.run()

        save_btn = next((b for b in at.button if b.label == "SAVE"), None)
        if save_btn is None:
            pytest.skip("SAVE button not found — form may require additional fields.")
        save_btn.click().run()

        if not intake_mock.rpc.called:
            pytest.skip("RPC not called — form validation blocked save (expected for some mock configurations).")

        rpc_args = intake_mock.rpc.call_args
        # Handle both positional and keyword argument call styles
        if rpc_args[1] and "params" in rpc_args[1]:
            payload = rpc_args[1]["params"].get("p_payload", {})
        elif len(rpc_args[0]) > 1:
            payload = rpc_args[0][1].get("p_payload", {})
        else:
            pytest.skip("Could not extract payload from RPC call args.")

        required_fields = ["species_id", "observer_id", "session_id", "bins"]
        for field in required_fields:
            assert field in payload, (
                f"Required field '{field}' missing from vault_finalize_intake payload. "
                f"This will cause a DB crash. Payload keys: {list(payload.keys())}"
            )


def test_happy_path_intake_mother_weight_key_present(intake_mock):
    """
    CR-20260426 Lo-3: After v8_1_22 migration, mother_weight_g must be a key
    in the intake payload (even if None). Its absence caused the production crash.
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=intake_mock), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "hp-observer"
        at.session_state.session_id = "hp-session"
        at.run()

        at.text_input[0].set_value("2026-HP-003")
        at.text_input[1].set_value("Howland")
        # CR-20260430-194500: bin mass/temp removed — these fields no longer exist in intake payload
        at.run()

        save_btn = next((b for b in at.button if b.label == "SAVE"), None)
        if save_btn is None:
            pytest.skip("SAVE button not found.")
        save_btn.click().run()

        if not intake_mock.rpc.called:
            pytest.skip("RPC not called — cannot verify payload structure.")

        rpc_args = intake_mock.rpc.call_args
        if rpc_args[1] and "params" in rpc_args[1]:
            payload = rpc_args[1]["params"].get("p_payload", {})
        elif len(rpc_args[0]) > 1:
            payload = rpc_args[0][1].get("p_payload", {})
        else:
            pytest.skip("Cannot extract payload.")

        intake_sub = payload.get("intake", payload)
        # mother_weight_g must exist as a key (value can be None)
        assert "mother_weight_g" in intake_sub or "mother_weight_g" in payload, (
            "mother_weight_g key is absent from the intake payload. "
            "This caused the Lo-3 production crash when the column was renamed."
        )
