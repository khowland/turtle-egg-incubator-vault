"""
=============================================================================
Module:     utils/session.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Session management, observer identity tracking, and session 
            audit logging.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
from datetime import datetime

# =============================================================================
# SECTION: Session ID Generation
# =============================================================================

def init_session(observer_id: str, display_name: str):
    """Generates a new session ID and stores observer state.
    
    Creates a Natural Key session ID: {observer_id}_{YYYYMMDDHHMMSS}.
    Initializes session_state keys for audit and UI behavior.
    
    Args:
        observer_id: The unique slug for the observer (e.g., 'elisa').
        display_name: The full name of the observer for the UI.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session_id = f"{observer_id}_{timestamp}"
    
    # Store in session state for cross-page persistence
    st.session_state["session_id"] = session_id
    st.session_state["observer_id"] = observer_id
    st.session_state["observer_name"] = display_name
    st.session_state["logged_in"] = True
    
    # Requirement: Log session start to SessionLog table
    # This usually happens in the sidebar selection logic

# -----------------------------------------------------------------------------
# Function: get_active_session
# Description: Returns current session ID or None if locked
# -----------------------------------------------------------------------------
def get_active_session():
    """Retrieves the current session ID from state.
    
    Returns:
        str or None: The active session_id if authenticated, else None.
    """
    return st.session_state.get("session_id")
