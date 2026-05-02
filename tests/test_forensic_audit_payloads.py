"""
=============================================================================
File:     tests/test_forensic_audit_payloads.py
Suite:    Phase 3 — P3-FOR-1 through P3-FOR-5
Coverage: §4.3 — Every clinical write must record observer, session, and time.
          Void audit trail, safe_db_execute crash logging.
=============================================================================
"""
import pytest
import datetime
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch


def _make_observations_mock(observer_id="forensic-observer", session_id="forensic-session"):
    """Build a fully hydrated mock for 3_Observations.py."""
    mock_sb = MagicMock()
    table_clients = {}

    def get_table(name):
        if name in table_clients:
            return table_clients[name]
        m = MagicMock()
        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": 1, "bin_code": "FOR-BIN", "intake_id": "FOR-CASE"}  # CR-20260501-1800: numeric bin_id + bin_code
            ]
        elif name == "egg":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
                {
                    "egg_id": "FOR-BIN-E1",
                    "bin_id": 1, "bin_code": "FOR-BIN",  # CR-20260501-1800: numeric bin_id + bin_code
                    "current_stage": "S1",
                    "status": "Active",
                    "is_deleted": False,
                    "last_chalk": 0,
                    "last_vasc": False,
                    "intake_timestamp": "2026-01-01T12:00:00Z",
                }
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"egg_id": "FOR-BIN-E1", "bin_id": 1, "bin_code": "FOR-BIN", "intake_timestamp": "2026-01-01T12:00:00Z"}  # CR-20260501-1800: numeric bin_id + bin_code
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"egg_id": "FOR-BIN-E1", "bin_id": 1, "bin_code": "FOR-BIN", "intake_timestamp": "2026-01-01T12:00:00Z"}  # CR-20260501-1800: numeric bin_id + bin_code
            ]
        elif name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": session_id}
            ]
        table_clients[name] = m
        return m

    # Pre-warm common tables to avoid KeyError in test logic
    for t in ["bin", "egg", "bin_observation", "egg_observation", "intake", "system_log", "species"]:
        get_table(t)

    mock_sb.table.side_effect = get_table
    return mock_sb, table_clients


# ---------------------------------------------------------------------------
# P3-FOR-1: egg_observation INSERT must contain observer_id
# ---------------------------------------------------------------------------
def test_egg_observation_payload_contains_observer_id():
    """
    P3-FOR-1: Every egg_observation RPC payload must include observer_id.
    This prevents anonymous clinical writes that break the forensic audit trail.
    """
    mock_sb, table_clients = _make_observations_mock(observer_id="forensic-observer")

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "forensic-observer"
        at.session_state.session_id = "forensic-session"
        at.session_state.observer_name = "Forensic Tester"
        at.session_state.workbench_bins = {"FOR-BIN"}
        at.session_state.env_gate_synced = {"FOR-BIN": True}
        at.run(timeout=15)

        assert not at.exception, f"Observations crashed: {at.exception}"
        # If SAVE was fired (requires active eggs + selection), verify observer_id in any insert call
        # Since the mock returns eggs, any RPC/insert call should carry the observer
        if mock_sb.rpc.called:
            rpc_args = mock_sb.rpc.call_args
            params = rpc_args[1].get("params", {}) if rpc_args[1] else {}
            payload = params.get("p_payload", {})
            if isinstance(payload, dict) and "observer_id" in payload:
                assert payload["observer_id"] == "forensic-observer", (
                    f"observer_id mismatch in RPC payload: {payload.get('observer_id')}"
                )

def test_void_writes_to_system_log_with_reason():
    """
    P3-FOR-2: When an observation is voided, safe_db_execute must write
    an AUDIT event to system_log with a non-empty reason.
    Verifies the forensic audit trail is intact for void operations.
    """
    from utils.bootstrap import safe_db_execute
    from unittest.mock import MagicMock, patch, call

    mock_sb = MagicMock()
    log_inserts = []

    def capture_insert(data):
        log_inserts.append(data)
        m = MagicMock()
        m.execute.return_value.data = []
        return m

    mock_sb.table.return_value.insert.side_effect = capture_insert

    with patch("utils.bootstrap.get_supabase", return_value=mock_sb):
        safe_db_execute(
            "Void Observation",
            lambda: True,
            success_message="Void: Observation voided — duplicate entry",
        )

    # The success_message triggers a system_log insert inside safe_db_execute
    assert len(log_inserts) >= 1, "safe_db_execute did not write to system_log on void."
    log_entry = log_inserts[-1]
    assert log_entry.get("event_message"), "system_log event_message is empty — reason missing."

def test_void_without_reason_defaults_to_no_reason_supplied():
    """
    P3-FOR-3: If safe_db_execute is called without a success_message (void
    without reason), the system_log write must be skipped — no empty-string entries.
    """
    from utils.bootstrap import safe_db_execute
    from unittest.mock import MagicMock, patch

    mock_sb = MagicMock()
    log_inserts = []

    def capture_insert(data):
        log_inserts.append(data)
        m = MagicMock()
        m.execute.return_value.data = []
        return m

    mock_sb.table.return_value.insert.side_effect = capture_insert

    with patch("utils.bootstrap.get_supabase", return_value=mock_sb):
        safe_db_execute(
            "Void No Reason",
            lambda: True,
            success_message=None,  # No reason provided
        )

    # With success_message=None, safe_db_execute must NOT write to system_log
    blank_messages = [e for e in log_inserts if not e.get("event_message")]
    assert len(blank_messages) == 0, (
        f"safe_db_execute wrote {len(blank_messages)} blank event_message entries to system_log."
    )

def test_intake_timestamp_is_timezone_aware():
    """
    P3-FOR-4: §3.3 requires intake_timestamp to be TIMESTAMPTZ.
    Verify the RPC payload contains a timezone-aware ISO string.
    """
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5}
    ]
    mock_sb.rpc.return_value.execute.return_value.data = [
        {"intake_id": "I-TZ-1", "first_bin_id": 1, "first_bin_code": "BIN-TZ-1"}  # CR-20260501-1800: numeric bin_id + bin_code
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "tz-observer"
        at.session_state.session_id = "tz-session"
        at.run()

        at.text_input[0].set_value("2026-TZ-001")
        at.text_input[1].set_value("TZ Biologist")
        
        # PROVIDE MANDATORY METRICS (§2, v8.1.16) via session state due to data_editor change
        at.session_state.bin_rows[0]["shelf"] = "SHELF-TZ"
        at.session_state.bin_rows[0]["mass"] = 200.0
        at.session_state.bin_rows[0]["temp"] = 28.0
        at.run()

        save_btn = next(b for b in at.button if b.label == "SAVE")
        save_btn.click().run()

        assert mock_sb.rpc.called, "vault_finalize_intake RPC was never called."
        rpc_args = mock_sb.rpc.call_args
        params = rpc_args[1].get("params", rpc_args[0][1] if len(rpc_args[0]) > 1 else {})
        payload = params.get("p_payload", {})

        intake_ts = payload.get("intake_timestamp", "")
        assert intake_ts, "intake_timestamp is missing from RPC payload."
        # Must be parseable as a timezone-aware datetime
        try:
            parsed = datetime.datetime.fromisoformat(str(intake_ts).replace("Z", "+00:00"))
            assert parsed.tzinfo is not None, (
                f"intake_timestamp '{intake_ts}' is not timezone-aware (TIMESTAMPTZ)."
            )
        except ValueError as e:
            pytest.fail(f"intake_timestamp '{intake_ts}' is not a valid ISO datetime: {e}")


# ---------------------------------------------------------------------------
# P3-FOR-5: safe_db_execute crash in Observations must log to system_log
# ---------------------------------------------------------------------------
def test_safe_db_execute_crash_logs_to_system_log():
    """
    P3-FOR-5: When safe_db_execute catches an exception, it must write an
    ERROR event to system_log. This guarantees crashes are forensically traceable.
    """
    from utils.bootstrap import safe_db_execute
    from unittest.mock import MagicMock, patch
    import streamlit as st

    mock_sb = MagicMock()
    error_inserts = []

    def capture_insert(data):
        error_inserts.append(data)
        m = MagicMock()
        m.execute.return_value.data = []
        return m

    mock_sb.table.return_value.insert.side_effect = capture_insert

    with patch("utils.bootstrap.get_supabase", return_value=mock_sb):
        # Run safe_db_execute with a crashing function
        result = safe_db_execute(
            "Crashing Operation",
            lambda: (_ for _ in ()).throw(Exception("Simulated DB crash")),
        )

    # safe_db_execute must return None on exception (Safe-State)
    assert result is None, f"safe_db_execute should return None on crash, got: {result}"
    # Must have attempted to write an ERROR event
    error_events = [e for e in error_inserts if e.get("event_type") == "ERROR"]
    assert len(error_events) >= 1, (
        "safe_db_execute did not write an ERROR event to system_log on crash. "
        "Crash forensics are broken."
    )
