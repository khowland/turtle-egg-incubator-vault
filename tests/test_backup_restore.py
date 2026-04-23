import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

@pytest.mark.skip(reason="file_uploader is not currently supported by Streamlit AppTest API in this environment.")
def test_json_restore_ui_logic():
    at = AppTest.from_file("vault_views/5_Settings.py")
    at.session_state.session_id = "test-session"
    at.session_state.observer_id = "00000000-0000-0000-0000-000000000000"
    at.session_state.backup_verified = True
    at.session_state.global_font_size = 18
    at.session_state.line_height = 1.6
    at.session_state.high_contrast = False
    at.run(timeout=15)

    # Upload File and verify button renders but is locked without text
    json_bytes = b'{"intake": [{"intake_id": "I-999"}]}'
    at.file_uploader[0].set_value([("winc_vault_full_backup.json", json_bytes, "application/json")])
    at.run(timeout=15)

    restore_btns = [b for b in at.button if "RESTORE FROM UPLOADED BACKUP" in b.label]
    assert len(restore_btns) == 1, "Restore button must be visible"
    assert restore_btns[0].disabled == True, "Must be locked without text confirmation"

    # Input exact confirmation
    at.text_input[0].input("OBLITERATE CURRENT DATA").run(timeout=15)

    restore_btns = [b for b in at.button if "RESTORE FROM UPLOADED BACKUP" in b.label]
    assert restore_btns[0].disabled == False, "Must unlock with confirmation and file payload"
