"""
=============================================================================
Module:     utils/session.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Observer session management and sidebar UI.
            Designed for non-technical wildlife staff — plain language,
            minimal controls, no confusing options.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Mobile-first: removed Lottie, simplified sidebar,
            plain language for volunteers)
=============================================================================
"""

import streamlit as st
from datetime import datetime
from utils.db import get_supabase_client
from utils.logger import logger

# =============================================================================
# SECTION: Session Initialization
# Description: Creates a unique session ID when a staff member selects their
#              name. This ID is attached to every record they create/edit
#              for accountability tracking.
# =============================================================================

def init_session(observer_id: str, display_name: str):
    """Creates a new session when a staff member selects their name.
    
    Generates a unique session ID and logs it to the SessionLog table
    so we can track who was working when.
    
    Args:
        observer_id: Short ID for the staff member (e.g., "elisa").
        display_name: Full name shown in the UI (e.g., "Elisa Rodriguez").
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session_id = f"{observer_id}_{timestamp}"
    st.session_state["session_id"] = session_id
    st.session_state["observer_id"] = observer_id
    st.session_state["observer_name"] = display_name
    st.session_state["logged_in"] = True
    
    logger.info(f"🔑 Session started: {display_name} ({session_id})")
    
    # Write session to database for audit trail
    try:
        supabase = get_supabase_client()
        supabase.table("SessionLog").insert({
            "session_id": session_id,
            "user_name": display_name,
        }).execute()
    except Exception as e:
        # Non-blocking — don't prevent staff from working if log table has issues
        logger.warning(f"SessionLog insert failed (non-blocking): {e}")

def get_active_session():
    """Returns the current session ID, or None if no one is logged in."""
    return st.session_state.get("session_id")

# =============================================================================
# SECTION: Sidebar
# Description: Simple sidebar with just two things:
#              1. Your name (who's working right now)
#              2. Current session ID (for troubleshooting only)
#              No animations, no refresh buttons, no clutter.
# =============================================================================

def render_sidebar():
    """Renders the sidebar — observer name picker and session info.
    
    Kept deliberately minimal for non-technical staff.
    No animations, no extra buttons, no jargon.
    """
    with st.sidebar:
        st.markdown("### 🐢 Incubator Vault")
        st.caption("Wildlife In Need Center")
        st.markdown("---")
        
        # --- WHO'S WORKING ---
        supabase = get_supabase_client()
        observers = []
        try:
            res = supabase.table("observer").select("*").eq("is_active", True).execute()
            observers = res.data if res.data else []
        except Exception as e:
            # Fallback if observer table doesn't exist yet
            logger.warning(f"Observer table query failed, using fallback: {e}")
            observers = [
                {"observer_id": "elisa", "display_name": "Elisa Rodriguez"},
                {"observer_id": "kevin", "display_name": "Kevin Howland"}
            ]
        
        obs_names = [o["display_name"] for o in observers]
        current_name = st.session_state.get("observer_name")
        
        selected_name = st.selectbox(
            "👤 Who's working?",
            options=["-- Pick your name --"] + obs_names,
            index=obs_names.index(current_name) + 1 if current_name in obs_names else 0
        )
        
        if selected_name != "-- Pick your name --":
            selected_id = next(o["observer_id"] for o in observers if o["display_name"] == selected_name)
            if st.session_state.get("observer_id") != selected_id:
                init_session(selected_id, selected_name)
                st.rerun()
        else:
            st.session_state["logged_in"] = False
            st.warning("⬆️ Pick your name to start.")

        # --- SESSION FOOTER ---
        st.markdown("---")
        sid = get_active_session()
        if sid:
            st.caption(f"Session: {sid}")
