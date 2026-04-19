import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone

@pytest.fixture
def mock_supabase():
    return MagicMock()

from tests.mock_utils import build_table_aware_mock

def test_session_recovery_boundary_valid():
    """
    RES-1: Test session recovery within the 4-hour window (3 hours 59 mins).
    """
    recent_time = (datetime.now(timezone.utc) - timedelta(hours=3, minutes=55)).isoformat().replace("+00:00", "Z")
    
    table_data = {
        "session_log": [{"session_id": "old-active-session", "login_timestamp": recent_time, "user_name": "Kevin"}],
        "system_log": [],
        "observer": [{"observer_id": "O1", "display_name": "Kevin", "is_active": True}]
    }
    mock_supabase, _ = build_table_aware_mock(table_data)

    with patch("utils.session.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/0_Login.py")
        at.run()
        
        # Submit login
        at.selectbox[0].select("Kevin")
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()
        
        # Should adopt the old session ID
        assert at.session_state.session_id == "old-active-session"

def test_session_recovery_boundary_expired():
    """
    RES-2: Test session recovery outside the 4-hour window (4 hours 1 min).
    """
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=4, minutes=5)).isoformat().replace("+00:00", "Z")
    table_data = {
        "session_log": [{"session_id": "stale-session", "login_timestamp": stale_time, "user_name": "Kevin"}],
        "system_log": [],
        "observer": [{"observer_id": "O1", "display_name": "Kevin", "is_active": True}]
    }
    mock_supabase, _ = build_table_aware_mock(table_data)
    
    with patch("utils.session.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/0_Login.py")
        at.run()
        
        at.selectbox[0].select("Kevin")
        # Use label filtering
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()
        
        # Should NOT adopt the stale session ID (it should be a new UUID)
        assert at.session_state.session_id != "stale-session"
        assert len(at.session_state.session_id) == 36 # UUID length

