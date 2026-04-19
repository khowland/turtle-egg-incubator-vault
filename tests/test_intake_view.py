import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_supabase():
    """Provides a mocked Supabase client."""
    mock_client = MagicMock()
    
    # Mock species table fetching
    mock_species_data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 5},
        {"species_id": 2, "species_code": "PC", "common_name": "Painted Turtle", "intake_count": 10}
    ]
    
    mock_client.table.return_value.select.return_value.execute.return_value.data = mock_species_data
    
    # Mock RPC for save
    mock_client.rpc.return_value.execute.return_value.data = {"first_bin_id": "SN6-KEVIN-1"}
    
    return mock_client

def test_intake_form_submission(mock_supabase):
    """
    Test that the New Intake form can be filled and submitted successfully.
    """
    # We need to patch the bootstrap_page to return our mock_supabase
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py", default_timeout=30)
        
        # Set session state before run
        at.session_state.observer_id = "test-observer"
        at.session_state.session_id = "test-session"
        
        at.run()
        
        # Verify UI components
        assert at.title[0].value == "🛡️ New Intake"
        
        # Fill the form
        at.text_input[0].set_value("2026-0001") # WINC Case #
        at.text_input[1].set_value("Kevin")     # Who found the turtle?
        at.text_input[2].set_value("Roadside")  # Where was she found?
        
        # Fill Bin Setup (mandatory fields for v8.1.16)
        at.number_input[1].set_value(1)         # egg_count (already 1, but set explicitly)
        at.text_input[3].set_value("A1")         # shelf_location
        at.number_input[2].set_value(150.5)     # mass
        at.number_input[3].set_value(28.5)      # temp
        
        # Select Species (SN - Snapping Turtle)
        # Check available options in the selectbox
        assert "SN - Snapping Turtle" in at.selectbox[0].options
        at.selectbox[0].select("SN - Snapping Turtle").run()
        
        # Submit the form
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Verify RPC was called
        assert mock_supabase.rpc.called
        
        # Verify redirect
        assert at.session_state.active_bin_id == "SN6-KEVIN-1"


def test_intake_validation_missing_fields(mock_supabase):
    """
    Verify that validation errors appear when required fields are missing.
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_supabase):
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "test-observer"
        at.session_state.session_id = "test-session"
        at.run()
        
        # Click SAVE without filling anything
        save_button = next(b for b in at.button if b.label == "SAVE")
        save_button.click().run()
        
        # Check for error message
        assert "Validation Failed: Please enter who found the turtle." in at.error[0].value
