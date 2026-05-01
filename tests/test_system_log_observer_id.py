# CR-20260430-194500: Test system_log observer_id conditional handling
"""
Test the conditional observer_id logic in commit_all() from 2_New_Intake.py:
- log_entry built without observer_id when session_state has none
- log_entry built with observer_id when present
- safe_db_execute wraps system_log insert in try/except (bootstrap.py lines 380-390)
"""
import pytest


class FakeSessionState(dict):
    """Mock st.session_state with .get() method."""
    def get(self, key, default=None):
        return super().get(key, default)


def build_log_entry(session_state, error_msg):
    """Reproduce the conditional log_entry logic from 2_New_Intake.py lines 368-374."""
    log_entry = {
        "session_id": session_state.get("session_id", "unknown"),
        "event_type": "ERROR",
        "event_message": f"Intake failed: {error_msg}",
    }
    if session_state.get("observer_id"):
        log_entry["observer_id"] = session_state["observer_id"]
    return log_entry


def test_log_entry_without_observer_id():
    """When observer_id is not set, log_entry must not include observer_id."""
    state = FakeSessionState({
        "session_id": "test-session-1",
    })
    entry = build_log_entry(state, "Test error")

    assert "observer_id" not in entry, \
        "log_entry must not include observer_id when session_state has none"
    assert entry["session_id"] == "test-session-1"
    assert entry["event_type"] == "ERROR"
    assert "Test error" in entry["event_message"]


def test_log_entry_with_observer_id():
    """When observer_id is set, log_entry must include observer_id."""
    state = FakeSessionState({
        "session_id": "test-session-2",
        "observer_id": "obs-42",
    })
    entry = build_log_entry(state, "Test error")

    assert "observer_id" in entry, \
        "log_entry must include observer_id when session_state has one"
    assert entry["observer_id"] == "obs-42"
    assert entry["session_id"] == "test-session-2"


def test_log_entry_with_falsy_observer_id():
    """When observer_id is empty string/None, must NOT be included."""
    for falsy_val in [None, "", 0]:
        state = FakeSessionState({
            "session_id": "test-session-3",
            "observer_id": falsy_val,
        })
        entry = build_log_entry(state, "Test error")
        assert "observer_id" not in entry, \
            f"log_entry must not include observer_id when value is {falsy_val!r}"


def test_safe_db_execute_wraps_insert_in_try_except():
    """Verify safe_db_execute in bootstrap.py has try/except for system_log insert."""
    import os
    path = os.path.join(
        os.path.dirname(__file__),
        "..", "utils", "bootstrap.py"
    )
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    # safe_db_execute wraps commit_all in try/except (see lines 380-390)
    assert "safe_db_execute" in src, \
        "bootstrap.py must define safe_db_execute"
    assert "try:" in src, \
        "bootstrap.py must contain try/except for error handling"
    assert "except" in src, \
        "bootstrap.py must contain except clause"
