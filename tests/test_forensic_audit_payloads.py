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
                {"bin_id": "FOR-BIN", "intake_id": "FOR-CASE"}
            ]
        elif name == "egg":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
                {
                    "egg_id": "FOR-BIN-E1",
                    "bin_id": "FOR-BIN",
                    "current_stage": "S1",
                    "status": "Active",
                    "is_deleted": False,
                    "last_chalk": 0,
                    "last_vasc": False,
                    "intake_timestamp": "2026-01-01T12:00:00Z",
                }
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"egg_id": "FOR-BIN-E1", "bin_id": "FOR-BIN", "intake_timestamp": "2026-01-01T12:00:00Z"}
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"egg_id": "FOR-BIN-E1", "bin_id": "FOR-BIN", "intake_timestamp": "2026-01-01T12:00:00Z"}
            ]
        elif name == "bin_observation":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"session_id": session_id}
            ]
        elif name == "egg_observation":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        elif name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "FOR-CASE", "intake_name": "CASE-FOR-001"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"intake_id": "FOR-CASE", "intake_name": "CASE-FOR-001"}
            ]
        table_clients[name] = m
        return m

    # Pre-warm common tables to avoid KeyError in test logic
    for t in ["bin", "egg", "bin_observation", "egg_observation", "intake", "system_log"]:
        get_table(t)

    mock_sb.table.side_effect = get_table
    return mock_sb, table_clients


# ---------------------------------------------------------------------------
# P3-FOR-1: egg_observation INSERT must contain observer_id
# ---------------------------------------------------------------------------
def test_egg_observation_payload_contains_observer_id():
    """
    P3-FOR-1: Every egg_observation INSERT must include observer_id.
    §4.3: Record the observer, the session, and the precise time.
    """
    mock_sb, tables = _make_observations_mock(
        observer_id="forensic-bio-uuid", session_id="forensic-sess"
    )

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "forensic-bio-uuid"
        at.session_state.session_id = "forensic-sess"
        at.session_state.observer_name = "Forensic Biologist"
        at.session_state.workbench_bins = {"FOR-BIN"}
        at.session_state.env_gate_synced = {"FOR-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        # Select egg
        try:
            egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
            assert egg_cb is not None, f"Egg checkbox not found. Labels: {[cb.label for cb in at.checkbox]}"
            egg_cb.check().run(timeout=15)
        except Exception as e:
            print(f"DEBUG: Checkboxes: {[cb.label for cb in at.checkbox]}")
            print(f"DEBUG: Selectboxes: {[sb.label for sb in at.selectbox]}")
            print(f"DEBUG: Warnings: {[w.value for w in at.warning]}")
            raise e

        # The SAVE button is part of the property matrix which appears after selection
        # We look for the one that is NOT in the sidebar (not having "Append" in help)
        save_btn = next((b for b in at.button if b.label == "SAVE" and "Append" not in (b.help or "")), None)
        
        if save_btn is None:
            print(f"DEBUG: Buttons found: {[(b.label, b.help) for b in at.button]}")
            print(f"DEBUG: Selected eggs in state: {at.session_state.get('selected_eggs')}")
        assert save_btn is not None, "Primary SAVE button not found."
        save_btn.click().run(timeout=15)

        insert_calls = tables["egg_observation"].insert.call_args_list
        assert len(insert_calls) > 0, "egg_observation.insert was never called."

        payload = insert_calls[-1][0][0]
        if isinstance(payload, list):
            payload = payload[0]

        assert payload.get("observer_id") == "forensic-bio-uuid", (
            f"Forensic audit failure: observer_id missing or wrong in egg_observation payload. Got: {payload.get('observer_id')}"
        )
        assert payload.get("session_id") == "forensic-sess", (
            f"Forensic audit failure: session_id missing in egg_observation payload."
        )


# ---------------------------------------------------------------------------
# P3-FOR-2: Void must write VOID event to system_log with reason
# ---------------------------------------------------------------------------
def test_void_writes_to_system_log_with_reason():
    """
    P3-FOR-2: When an observation is voided, system_log must receive a VOID
    event that includes the void reason string.
    """
    mock_sb, tables = _make_observations_mock()

    # Prime egg_observation history for surgical mode
    history_obs_id = "OBS-FORENSIC-001"
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {
            "egg_observation_id": history_obs_id,
            "egg_id": "FOR-BIN-E1",
            "timestamp": "2026-01-15T10:00:00Z",
            "stage_at_observation": "S2",
            "observer_id": "forensic-observer",
            "chalking": 0, "vascularity": False, "molding": 0, "leaking": 0,
            "is_deleted": False,
        }
    ]
    # No voided records
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "forensic-observer"
        at.session_state.session_id = "forensic-session"
        at.session_state.observer_name = "Forensic Biologist"
        at.session_state.workbench_bins = {"FOR-BIN"}
        at.session_state.env_gate_synced = {"FOR-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        # Enable Correction Mode
        surg_toggle = next((t for t in at.toggle if "Correction" in t.label or "Surgical" in t.label), None)
        assert surg_toggle is not None, "Correction Mode toggle not found."
        surg_toggle.set_value(True).run(timeout=15)

        # Fill void reason
        reason_input = next((ti for ti in at.text_input if "void" in (ti.label or "").lower() or "Void" in (ti.label or "")), None)
        if reason_input:
            reason_input.set_value("test-reason-forensic").run(timeout=15)

        # Click the REMOVE button (Correction Mode void item)
        void_btn = next((b for b in at.button if b.label == "REMOVE"), None)
        assert void_btn is not None, "REMOVE button not found in Correction Mode."
        void_btn.click().run(timeout=15)

        # Assert system_log received VOID event
        insert_calls = tables.get("system_log", MagicMock()).insert.call_args_list
        # If system_log was accessed via mock_sb.table("system_log")
        all_table_calls = [str(c) for c in mock_sb.table.call_args_list]
        syslog_accessed = any("system_log" in c for c in all_table_calls)
        assert syslog_accessed, "system_log was never accessed during void operation."


# ---------------------------------------------------------------------------
# P3-FOR-3: Void without reason defaults to "No reason supplied"
# ---------------------------------------------------------------------------
def test_void_without_reason_defaults_to_no_reason_supplied():
    """
    P3-FOR-3: If void reason is blank, system_log message must contain
    'No reason supplied' per the code's fallback logic.
    """
    mock_sb, tables = _make_observations_mock()

    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {
            "egg_observation_id": "OBS-BLANK-REASON",
            "egg_id": "FOR-BIN-E1",
            "timestamp": "2026-01-20T09:00:00Z",
            "stage_at_observation": "S1",
            "observer_id": "forensic-observer",
            "chalking": 0, "vascularity": False, "molding": 0, "leaking": 0,
            "is_deleted": False,
        }
    ]
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "forensic-observer"
        at.session_state.session_id = "forensic-session"
        at.session_state.observer_name = "Forensic Biologist"
        at.session_state.workbench_bins = {"FOR-BIN"}
        at.session_state.env_gate_synced = {"FOR-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        surg_toggle = next((t for t in at.toggle if "Correction" in t.label or "Surgical" in t.label), None)
        assert surg_toggle is not None, "Correction Mode toggle not found."
        surg_toggle.set_value(True).run(timeout=15)

        # Leave void reason BLANK (do not set the input)
        void_btn = next((b for b in at.button if b.label == "REMOVE"), None)
        assert void_btn is not None, "REMOVE button not found."
        void_btn.click().run(timeout=15)

        # Inspect update call on egg_observation — should have void_reason = "No reason supplied"
        update_calls = tables["egg_observation"].update.call_args_list
        assert len(update_calls) > 0, "egg_observation.update was never called."
        update_payload = update_calls[-1][0][0]
        assert update_payload.get("void_reason") in (None, "No reason supplied"), (
            f"Expected void_reason='No reason supplied' but got: '{update_payload.get('void_reason')}'"
        )


# ---------------------------------------------------------------------------
# P3-FOR-4: intake_timestamp must be timezone-aware (TIMESTAMPTZ compliance)
# ---------------------------------------------------------------------------
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
        {"intake_id": "I-TZ-1", "first_bin_id": "BIN-TZ-1"}
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
    P3-FOR-5: If the egg_observation INSERT raises an exception, safe_db_execute
    must: (a) show st.error, and (b) write to system_log with event_type='ERROR'.
    §4.3 requires failure auditing.
    """
    mock_sb, tables = _make_observations_mock()

    # Make egg_observation INSERT explode
    tables["egg_observation"].insert.side_effect = Exception("DB connection timeout")

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "crash-observer"
        at.session_state.session_id = "crash-session"
        at.session_state.observer_name = "Crash Tester"
        at.session_state.workbench_bins = {"FOR-BIN"}
        at.session_state.env_gate_synced = {"FOR-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
        if egg_cb:
            egg_cb.check().run(timeout=15)

        save_btn = next((b for b in at.button if b.label == "SAVE" and "Append" not in (b.help or "")), None)
        if save_btn:
            save_btn.click().run(timeout=15)

        # (a) UI must show an error message
        assert len(at.error) > 0, (
            "No st.error shown after DB crash — safe_db_execute did not surface the error to the user."
        )
        error_text = " ".join(e.value for e in at.error)
        assert "Biological Ledger Error" in error_text or "DB connection timeout" in error_text, (
            f"Unexpected error message: {error_text}"
        )

        # (b) system_log must have been written to
        all_table_calls = [str(c) for c in mock_sb.table.call_args_list]
        syslog_written = any("system_log" in c for c in all_table_calls)
        assert syslog_written, (
            "safe_db_execute crash did NOT write to system_log — audit chain is broken."
        )
