import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

@pytest.fixture
def mock_supabase():
    return MagicMock()

def test_session_recovery_boundary_valid(mock_supabase):
    """
    RES-1: Test session recovery within the 4-hour window (3 hours 59 mins).
    """
    # Mock existing session in DB from 3 hours 55 mins ago
    recent_time = (datetime.now() - timedelta(hours=3, minutes=55)).isoformat()
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"session_id": "old-active-session", "login_timestamp": recent_time, "user_name": "Kevin"}
    ]
    # Mock no termination record
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []

    with patch("utils.session.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/0_Login.py")
        # Mock active observers
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"observer_id": "O1", "display_name": "Kevin", "is_active": True}
        ]
        at.run()
        
        # Submit login - widgets inside form are accessible globally
        at.selectbox[0].select("Kevin")
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()
        
        # Should adopt the old session ID
        assert at.session_state.session_id == "old-active-session"

def test_session_recovery_boundary_expired(mock_supabase):
    """
    RES-2: Test session recovery outside the 4-hour window (4 hours 1 min).
    """
    # Mock old session from 4 hours 5 mins ago
    stale_time = (datetime.now() - timedelta(hours=4, minutes=5)).isoformat()
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"session_id": "stale-session", "login_timestamp": stale_time, "user_name": "Kevin"}
    ]
    
    with patch("utils.session.get_supabase", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/0_Login.py")
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"observer_id": "O1", "display_name": "Kevin", "is_active": True}
        ]
        at.run()
        
        at.selectbox[0].select("Kevin")
        # Use label filtering
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()
        
        # Should NOT adopt the stale session ID (it should be a new UUID)
        assert at.session_state.session_id != "stale-session"
        assert len(at.session_state.session_id) == 36 # UUID length
