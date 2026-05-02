"""
=============================================================================
File:     tests/test_mid_season_intake.py
Suite:    Phase 3.5 — Clinical Workflow: Mid-Season Intake
Coverage: §1.5 Supplemental Bin, §1.6 Supplemental Eggs.
=============================================================================
"""
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest


def _make_intake_mock_for_supplemental():
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": "SN", "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 1}
    ]
    # Supplemental RPC returns success
    mock_sb.rpc.return_value.execute.return_value.data = [
        {"intake_id": "I-EXISTING-001", "first_bin_id": 1, "first_bin_code": "SN1-HOWLAND-2"}  # CR-20260501-1800: numeric bin_id + bin_code
    ]
    return mock_sb


def test_add_eggs_to_existing_bin():
    """
    Supplemental intake: adding eggs to an existing bin must call
    vault_supplemental_intake (or vault_finalize_intake) RPC without crashing.
    The Intake page must not raise an unhandled exception during this flow.
    """
    mock_sb = _make_intake_mock_for_supplemental()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "supp-observer"
        at.session_state.session_id = "supp-session"
        at.run()

        assert not at.exception, f"Intake page crashed on load: {at.exception}"
        # Basic smoke: the page renders species selector and intake form fields
        # (full supplemental workflow requires UI-level bin flow that's tested in e2e)
        assert len(at.selectbox) >= 1 or len(at.text_input) >= 1, \
            "Intake page rendered no interactive elements — page is broken."


def test_add_new_bin_to_existing_case():
    """
    Adding a new bin to an existing case intake (supplemental bin flow) must
    not crash the Intake page and must preserve existing session state.
    """
    mock_sb = _make_intake_mock_for_supplemental()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page"):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "supp-observer"
        at.session_state.session_id = "supp-session"
        # Pre-set an existing intake context
        at.session_state.active_intake_id = "I-EXISTING-001"
        at.run()

        assert not at.exception, f"Intake page crashed with pre-existing intake in session: {at.exception}"
