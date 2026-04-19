import pytest
from unittest.mock import MagicMock, patch
from scripts.heartbeat_ping import trigger_heartbeat

def test_supabase_wake_on_503():
    """
    Simulate a 'Paused' Supabase project (503 error) and verify that 
    the heartbeat/wake script attempts recovery and handles the error correctly.
    """
    mock_sb = MagicMock()
    # Simulate a 503 Service Unavailable
    mock_sb.table.side_effect = Exception("503: Service Unavailable (Project Paused)")
    
    with patch("scripts.heartbeat_ping.create_client", return_value=mock_sb), \
         patch("scripts.heartbeat_ping.load_dotenv"):
        
        # This should attempt the ping and catch the exception gracefully
        # In a real 'wake' scenario, the request itself triggers the wake-up
        try:
            trigger_heartbeat()
            # If the script finishes without crashing, it caught the error
        except Exception as e:
            pytest.fail(f"Heartbeat script did not catch the connection error: {e}")

def test_supabase_wake_success():
    """
    Verify that the heartbeat script succeeds when the project is awake.
    """
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.count = 42
    
    with patch("scripts.heartbeat_ping.create_client", return_value=mock_sb), \
         patch("scripts.heartbeat_ping.load_dotenv"), \
         patch("os.getenv", side_effect=lambda k: "FAKE_VAL"):
        
        # This should print success message
        trigger_heartbeat()
        assert mock_sb.table.called
        assert mock_sb.table.return_value.select.called

def test_db_check_connection_resilience():
    """
    Verify that check_connection triggers wake_supabase_project on 503 error.
    """
    from utils.db import check_connection
    
    mock_sb = MagicMock()
    # First call: 503
    # Subsequent calls (during wait_for_restoration polling): Success
    mock_sb.table.return_value.select.return_value.limit.return_value.execute.side_effect = [
        Exception("503: Service Unavailable"),
        MagicMock(data=[{"species_id": 1}])
    ]
    
    with patch("utils.db.st.warning") as mock_st_warning, \
         patch("utils.supabase_mgmt.wake_supabase_project", return_value=True) as mock_wake, \
         patch("utils.supabase_mgmt.wait_for_restoration", side_effect=lambda f, **kwargs: f()) as mock_wait:
         
        result = check_connection(mock_sb)
        
        assert result is True
        assert mock_wake.called
        assert mock_st_warning.called

if __name__ == "__main__":
    pytest.main([__file__])
