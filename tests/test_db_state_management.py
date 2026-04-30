import pytest
import streamlit as st
import uuid
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
from utils.db import get_supabase

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
_DIRTY_INTAKE_ID = "I-TEST-GATE-001"
_DIRTY_SESSION_ID = "session-gate-test"
_DIRTY_OBSERVER_ID = "ebe72de7-345d-4335-94f3-63b2b64c7857"  # Kevin Howland (valid observer)


@pytest.fixture(autouse=False)
def dirty_db_state():
    """Create a minimal intake to make the DB 'dirty', then clean up."""
    sb = get_supabase()
    # Insert a minimal session_log entry first (FK dependency)
    # Insert a minimal session_log entry first (FK dependency)
    # Use ignore_duplicates=True (ON CONFLICT DO NOTHING) to avoid the broken
    # sync_modified_at trigger on session_log (session_log has no modified_at column)
    try:
        sb.table("session_log").upsert({
            "session_id": _DIRTY_SESSION_ID,
            "user_name": "TestGateUser",
            "user_agent": "WINC Test Suite",
        }, ignore_duplicates=True).execute()
    except Exception:
        pass

    # Insert a minimal intake record to make DB dirty
    try:
        sb.table("intake").insert({
            "intake_id": _DIRTY_INTAKE_ID,
            "intake_name": "TEST-GATE-INTAKE",
            "finder_turtle_name": "TestFinder",
            "species_id": "SN",
            "intake_date": "2026-01-01",
            "session_id": _DIRTY_SESSION_ID,
            "created_by_id": _DIRTY_OBSERVER_ID,
            "modified_by_id": _DIRTY_OBSERVER_ID,
        }).execute()
    except Exception:
        pass

    yield  # test runs here

    # Teardown: remove the test intake
    try:
        sb.table("intake").delete().eq("intake_id", _DIRTY_INTAKE_ID).execute()
    except Exception:
        pass


def test_backup_gate_locks_destructive_actions(dirty_db_state):
    st.cache_resource.clear()

    at = AppTest.from_file("vault_views/5_Settings.py")
    at.session_state.session_id = _DIRTY_SESSION_ID
    at.session_state.observer_id = _DIRTY_OBSERVER_ID
    at.session_state.global_font_size = 18
    at.session_state.line_height = 1.6
    at.session_state.high_contrast = False
    at.run(timeout=10)

    # Tabs don't need manual selection in AppTest; elements are parsed globally
    text_input = [t for t in at.text_input if "OBLITERATE" in t.label][0]
    assert text_input.disabled == True, "Text input must be locked before backup"

    wipe_clean_btn = [b for b in at.button if "WIPE & SET CLEAN START" in b.label][0]
    wipe_seed_btn = [b for b in at.button if "WIPE & SEED" in b.label][0]
    assert wipe_clean_btn.disabled == True, "Clean Wipe button must be locked"
    assert wipe_seed_btn.disabled == True, "Seed Wipe button must be locked"


@patch("utils.db.get_supabase_client")
def test_backup_gate_unlocks_after_backup_and_confirmation(mock_get_supabase):
    st.cache_resource.clear()
    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase

    mock_res = MagicMock()
    mock_res.data = [{"intake_id": "I-123"}]
    mock_supabase.table().select().limit().execute.return_value = mock_res

    at = AppTest.from_file("vault_views/5_Settings.py")
    at.session_state.session_id = "test-session"
    at.session_state.observer_id = "00000000-0000-0000-0000-000000000000"
    at.session_state.backup_verified = True 
    at.session_state.global_font_size = 18
    at.session_state.line_height = 1.6
    at.session_state.high_contrast = False
    at.run(timeout=10)
    
    # Tabs don't need manual selection in AppTest; elements are parsed globally
    text_input = [t for t in at.text_input if "OBLITERATE" in t.label][0]
    assert text_input.disabled == False, "Text input should unlock after backup"

    wipe_clean_btn = [b for b in at.button if "WIPE & SET CLEAN START" in b.label][0]
    assert wipe_clean_btn.disabled == True, "Buttons should stay locked without exact confirmation string"

    # Simulate user typing confirmation
    at.text_input[0].input("OBLITERATE CURRENT DATA").run(timeout=10)

    # Security Gate verified: Button only unlocks when confirmation string is matched
    wipe_clean_btn = [b for b in at.button if "WIPE & SET CLEAN START" in b.label][0]
    assert wipe_clean_btn.disabled == False, "Button must unlock with exact confirmation"
