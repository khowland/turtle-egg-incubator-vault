import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_supabase():
    with patch("utils.db.get_supabase") as mock:
        client = MagicMock()
        mock.return_value = client
        
        # Default mock responses to represent clean system state
        mock_res = MagicMock()
        mock_res.data = []
        mock_res.count = 0
        client.table().select().execute.return_value = mock_res
        client.table().select().eq().execute.return_value = mock_res
        client.table().select().order().execute.return_value = mock_res
        client.table().select().eq().order().limit().execute.return_value = mock_res
        client.table().select().or_().execute.return_value = mock_res
        client.table().upsert().execute.return_value = mock_res
        client.table().insert().execute.return_value = mock_res
        client.table().update().execute.return_value = mock_res
        # Mock soft-delete (update is_deleted) for delete operations
        client.table().update().execute.return_value = mock_res
        client.rpc().execute.return_value = mock_res
        
        # Mock observers for login
        client.table("observer").select().eq().execute.return_value.data = [
            {"observer_id": "test-id", "display_name": "Test User", "is_active": True}
        ]
        
        # Mock version
        client.table("system_config").select().eq().execute.return_value.data = [
            {"config_value": "v8.2.1"}
        ]
        
        # Mock bins for dashboard
        client.table("bin").select().eq().execute.return_value.data = [
            {"bin_id": "BIN-001", "is_deleted": False}
        ]
        
        yield client

def test_all_pages_smoke_check(mock_supabase):
    """
    REQ: Verify all menu screens load without NameError, AttributeError, or visible exceptions.
    """
    pages = [
        "vault_views/0_Login.py",
        "vault_views/1_Dashboard.py",
        "vault_views/2_New_Intake.py",
        "vault_views/3_Observations.py",
        "vault_views/5_Settings.py",
        "vault_views/6_Reports.py",
        "vault_views/7_Diagnostic.py",
        "vault_views/8_Help.py"
    ]
    
    for page_path in pages:
        at = AppTest.from_file(page_path)
        
        # Setup session state to bypass login and hydration gates
        at.session_state.observer_id = "test-id"
        at.session_state.observer_name = "Test User"
        at.session_state.session_id = "test-session"
        at.session_state.workbench_bins = {"BIN-001"}
        at.session_state.active_bin_id = "BIN-001"
        at.session_state.surgical_resurrection = False
        at.session_state.env_gate_synced = {"BIN-001": True}
        
        at.run(timeout=10)
        
        # Check for common error indicators in the rendered UI
        # Streamlit AppTest doesn't have a direct "exception" check easily, 
        # but we can look at the markdown and error elements.
        
        # 1. Check for st.error or red-box error messages
        assert not at.exception, f"Crash detected in {page_path}: {at.exception}"
        
        # 2. Check for redacted error message string (WINC Standard)
        redacted_msg = "This app has encountered an error. The original error message is redacted"
        for msg in at.markdown:
            assert redacted_msg not in msg.value, f"Redacted error found in {page_path}"
        
        # 3. Check for specific NameError/AttributeError strings if they leak
        for msg in at.markdown:
            assert "NameError" not in msg.value, f"NameError leak in {page_path}"
            assert "AttributeError" not in msg.value, f"AttributeError leak in {page_path}"
