"""
=============================================================================
File:     tests/test_session_termination.py
Suite:    Phase 3 — P3-SES-1, P3-SES-2, P3-SES-3
Coverage: §2.1 (expiry boundary), §2.2 (SHIFT END gate / TERMINATE flag)
=============================================================================
"""
import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, call
from streamlit.testing.v1 import AppTest


@pytest.fixture
def mock_supabase():
    return MagicMock()


# ---------------------------------------------------------------------------
# P3-SES-1: Session expiry (> 4 hours) MUST generate a new UUID
# Replaces the `pass` stub in test_session_boundaries.py::test_session_expiry_boundary
# ---------------------------------------------------------------------------
def test_session_expiry_creates_new_id(mock_supabase):
    """
    P3-SES-1: A session older than 4 hours must NOT be re-adopted at login.
    §36: Within 4 hours? Resume. Outside? New session.
    """
    stale_time = (datetime.now() - timedelta(hours=4, minutes=10)).isoformat()
    stale_id = "stale-expired-session-id"

    # Mock: session_log returns a stale session
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"session_id": stale_id, "login_timestamp": stale_time, "user_name": "Kevin"}
    ]
    # Mock: active observers
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"observer_id": "O1", "display_name": "Kevin", "is_active": True}
    ]
    # Mock: no TERMINATE event for the stale session
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

    with patch("utils.session.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/0_Login.py")
        at.run()

        at.selectbox[0].select("Kevin")
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()

        # Must NOT adopt the stale session
        assert at.session_state.session_id != stale_id, (
            f"Security Violation: Expired session '{stale_id}' was re-adopted after 4-hour window."
        )
        # Must be a valid UUID
        assert len(at.session_state.session_id) == 36, (
            "New session_id is not a valid UUID."
        )


# ---------------------------------------------------------------------------
# P3-SES-2: SHIFT END button must write TERMINATE to system_log
# ---------------------------------------------------------------------------
def test_shift_end_sets_terminate_flag():
    """
    P3-SES-2: Clicking SHIFT END must:
      (a) INSERT to system_log with event_type='TERMINATE'
      (b) Clear observer_id from session_state
    """
    mock_supabase = MagicMock()
    mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()

    with patch("utils.bootstrap.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/7_Diagnostic.py")
        at.session_state.observer_id = "biologist-001"
        at.session_state.session_id = "active-shift-session"
        at.session_state.observer_name = "Kevin"
        at.run()


        shift_end_btn = next(
            (b for b in list(at.button) + list(at.sidebar.button) if b.label == "SHIFT END"), None
        )
        assert shift_end_btn is not None, "SHIFT END button not found in sidebar."
        shift_end_btn.click().run()

        # (a) Verify TERMINATE event was written to system_log
        all_insert_calls = mock_supabase.table.return_value.insert.call_args_list
        terminate_calls = [
            c for c in all_insert_calls
            if isinstance(c[0][0], dict) and c[0][0].get("event_type") == "TERMINATE"
        ]
        assert len(terminate_calls) >= 1, (
            "SHIFT END did not write event_type='TERMINATE' to system_log."
        )

        # (b) Verify observer is cleared from session
        assert getattr(at.session_state, "observer_id", None) is None, (
            "observer_id was NOT cleared after SHIFT END."
        )


# ---------------------------------------------------------------------------
# P3-SES-3: A TERMINATED session (< 4 hrs old) must NOT be re-adopted
# ---------------------------------------------------------------------------
def test_terminated_session_not_resumed(mock_supabase):
    """
    P3-SES-3: Even if a session is within the 4-hour window, if it has a
    TERMINATE record in system_log, it must NOT be resumed.
    """
    recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
    terminated_id = "terminated-recent-session"

    # Mock: session_log returns a recent session (within 4 hrs)
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"session_id": terminated_id, "login_timestamp": recent_time, "user_name": "Kevin"}
    ]
    # Mock: active observers
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"observer_id": "O1", "display_name": "Kevin", "is_active": True}
    ]
    # Mock: system_log HAS a TERMINATE event for this session
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {"id": "log-001"}  # Non-empty = terminated
    ]

    with patch("utils.session.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/0_Login.py")
        at.run()

        at.selectbox[0].select("Kevin")
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()

        # Even though < 4 hours, TERMINATE flag means a fresh session must be created
        assert at.session_state.session_id != terminated_id, (
            f"Security Violation: Terminated session '{terminated_id}' was re-adopted "
            "despite TERMINATE record in system_log."
        )
        assert len(at.session_state.session_id) == 36, (
            "New session_id is not a valid UUID after terminated-session rejection."
        )
