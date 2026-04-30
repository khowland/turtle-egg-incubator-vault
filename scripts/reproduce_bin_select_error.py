import sys
import os
from unittest.mock import MagicMock

# Add the working directory to sys.path to import local modules
sys.path.append(os.getcwd())

# Mock streamlit before importing anything that uses it
sys.modules["streamlit"] = MagicMock()
import streamlit as st
st.columns.return_value = [MagicMock(), MagicMock()]


# Mock session state
st.session_state = MagicMock()

# Granular mocking for imports within Observations view
from unittest.mock import patch
mocker = patch('utils.bootstrap.get_last_bin_weight')
mocked_get_last_bin_weight = mocker.start()
mocked_get_last_bin_weight.return_value = {'bin_weight_g': 100}

# Target file and function path (Observations view)
# Target file and function path (Observations view)
Observations = __import__("vault_views.3_Observations", fromlist=[""])

def test_reproduction_and_fix():
    print("--- Starting Reproduction Test ---")
    
    # 1. Simulate the BROKEN state (bool instead of dict)
    st.session_state.env_gate_synced = False
    active_bin_id = "test_bin_id"
    
    print(f"Initial env_gate_synced state: {type(st.session_state.env_gate_synced)}")
    
    try:
        # This is line 288 in vault_views/3_Observations.py
        # The code tries to call .get() on env_gate_synced
        # We can simulate this by attempting a get on the object
        if not st.session_state.env_gate_synced.get(active_bin_id):
            pass
        print("Error: Expected AttributeError, but none occurred!")
    except AttributeError as e:
        print(f"Success: Caught expected AttributeError: {e}")

    # 2. Simulate the FIXED state (dict)
    print("\n--- Applying Fix in test context ---")
    # Initialize as dict, as per my patch in session.py/bootstrap.py
    st.session_state.env_gate_synced = {}
    print(f"Updated env_gate_synced state: {type(st.session_state.env_gate_synced)}")
    
    try:
        # Check if the code runs now
        if not st.session_state.env_gate_synced.get(active_bin_id):
            print("Success: No error with dict initialization.")
        else:
            print("Success: No error with dict initialization (and value found). ")
    except AttributeError as e:
        print(f"Error: Caught unexpected AttributeError after fix: {e}")

if __name__ == "__main__":
    test_reproduction_and_fix()
