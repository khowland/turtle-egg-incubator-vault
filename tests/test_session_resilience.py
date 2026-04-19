import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
from tests.mock_utils import build_table_aware_mock

@pytest.fixture
def mock_supabase():
    return MagicMock()

def test_session_recovery_boundary_valid():
    """
    RES-1: Test session recovery within the 4-hour window (3 hours 55 mins).
    """
    now_utc = datetime.now(timezone.utc)
    recent_time = (now_utc - timedelta(hours=3, minutes=55)).isoformat().replace("+00:00", "Z")
    old_active_session = "old-active-session"
    
    table_data = {
        "session_log": [{"session_id": old_active_session, "login_timestamp": recent_time, "user_name": "Kevin"}],
        "system_log": [],
        "observer": [{"observer_id": "O1", "display_name": "Kevin", "is_active": True}]
    }
    mock_sb, tables = build_table_aware_mock(table_data)

    # Patch ALL possible ways session.py might get the client
    with patch("utils.session.get_supabase", return_value=mock_sb), \
         patch("utils.session.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_supabase", return_value=mock_sb):
        
        at = AppTest.from_file("vault_views/0_Login.py")
        at.run()
        
        # Select observer and click START
        # (Assuming index 0 is Kevin based on our mock data)
        at.selectbox[0].select("Kevin").run()
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()
        
        if at.exception:
            raise at.exception[0]

        # Must adopt the old session ID
        actual_sid = at.session_state.session_id
        assert actual_sid == old_active_session, (
            f"Security Error: Failed to re-adopt valid session '{old_active_session}' within the 4-hour window. Found: {actual_sid}"
        )

def test_session_recovery_boundary_expired():
    """
    RES-2: Test session recovery outside the 4-hour window (4 hours 5 min).
    """
    now_utc = datetime.now(timezone.utc)
    stale_time = (now_utc - timedelta(hours=4, minutes=5)).isoformat().replace("+00:00", "Z")
    table_data = {
        "session_log": [{"session_id": "stale-session", "login_timestamp": stale_time, "user_name": "Kevin"}],
        "system_log": [],
        "observer": [{"observer_id": "O1", "display_name": "Kevin", "is_active": True}]
    }
    mock_sb, _ = build_table_aware_mock(table_data)
    
    with patch("utils.session.get_supabase", return_value=mock_sb), \
         patch("utils.session.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_supabase", return_value=mock_sb):
        
        at = AppTest.from_file("vault_views/0_Login.py")
        at.run()
        
        at.selectbox[0].select("Kevin").run()
        start_button = next(b for b in at.button if b.label == "START")
        start_button.click().run()
        
        # Should NOT adopt the stale session ID
        assert at.session_state.session_id != "stale-session"
        assert len(at.session_state.session_id) == 36 # New UUID
