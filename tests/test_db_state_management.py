import pytest
import streamlit as st
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest

@patch("utils.db.get_supabase_client")
def test_backup_gate_locks_destructive_actions(mock_get_supabase):
    st.cache_resource.clear()
    mock_supabase = MagicMock()
    mock_get_supabase.return_value = mock_supabase

    mock_res = MagicMock()
    mock_res.data = [{"intake_id": "I-123"}]
    mock_supabase.table().select().limit().execute.return_value = mock_res

    at = AppTest.from_file("vault_views/5_Settings.py")
    at.session_state.session_id = "test-session"
    at.session_state.observer_id = "00000000-0000-0000-0000-000000000000"
    at.session_state.global_font_size = 18
    at.session_state.line_height = 1.6
    at.session_state.high_contrast = False
    at.run(timeout=10)

    text_input = at.text_input[0]
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

    text_input = at.text_input[0]
    assert text_input.disabled == False, "Text input should unlock after backup"

    wipe_clean_btn = [b for b in at.button if "WIPE & SET CLEAN START" in b.label][0]
    assert wipe_clean_btn.disabled == True, "Buttons should stay locked without exact confirmation string"

    # Simulate user typing confirmation
    at.text_input[0].input("OBLITERATE CURRENT DATA").run(timeout=10)

    # Security Gate verified: Button only unlocks when confirmation string is matched
    wipe_clean_btn = [b for b in at.button if "WIPE & SET CLEAN START" in b.label][0]
    assert wipe_clean_btn.disabled == False, "Button must unlock with exact confirmation"
