import pytest
from streamlit.testing.v1 import AppTest

def test_login_screen_loads():
    """
    Verify that the login screen renders the splash header and user selectbox.
    """
    at = AppTest.from_file("vault_views/0_Login.py")
    at.run()
    
    # Assertions
    # 1. Check if the 'Select Your Name' text exists
    assert at.selectbox("Select Your Name") is not None
    
def test_dashboard_access_denied_without_auth():
    """
    Verify that the Dashboard page redirects or fails if no observer_id is set.
    """
    at = AppTest.from_file("vault_views/1_Dashboard.py")
    at.run()
    
    # If app logic calls st.stop() when no ID is found, checking for certain UI helps
    assert not at.subheader.exists("Shift Summary")
