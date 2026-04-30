import streamlit as st
from streamlit.testing.v1 import AppTest
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

def test_ui_intake_real_db():
    print("Starting UI Intake Reproduction Test with REAL DB...")
    
    # We use app.py as the entry point
    at = AppTest.from_file("app.py")
    
    # Mock the login state since we want to skip the UI login but use real DB
    at.session_state.observer_id = "ebe72de7-345d-4335-94f3-63b2b64c7857" # Kevin
    at.session_state.observer_name = "Kevin Howland"
    at.session_state.session_id = f"test-real-db-{uuid.uuid4().hex[:8]}"
    
    # Navigate to Intake
    at.run()
    at.switch_page("vault_views/2_New_Intake.py").run()
    
    # Fill form
    # Note: selectbox labels must match EXACTLY what's in the DB
    # We know 'BL - Blanding''s Turtle' is a common one
    try:
        at.selectbox(label="Species").set_value("BL - Blanding's Turtle").run()
    except Exception as e:
        print(f"Species selection failed (maybe label mismatch): {e}")
        # Try a simpler way if needed, but let's assume this works if Phase 1 passed
    
    at.text_input(label="WINC Case #").set_value("REPRO-001").run()
    at.text_input(label="Finder").set_value("Reproduction Runner").run()
    
    # Set bin data in session state directly for speed
    at.session_state.bin_rows = [{
        "bin_num": 1,
        "egg_count": 10,
        "mass": 150.5,
        "temp": 82.5,
        "notes": "Reproduction Test",
        "substrate": "Vermiculite",
        "shelf": "Shelf-R1"
    }]
    
    # Click SAVE
    print("Clicking SAVE...")
    at.button(key="intake_save").click().run(timeout=30)
    
    # Check for exceptions
    if at.exception:
        print(f"CRASH DETECTED: {at.exception}")
    
    # Check for error status in UI
    # In 2_New_Intake.py, st.error is used.
    # AppTest can find these via 'at.error' or markdown
    for err in at.error:
        print(f"UI ERROR MESSAGE: {err.value}")
    
    print("Reproduction Test Finished.")

if __name__ == "__main__":
    test_ui_intake_real_db()
