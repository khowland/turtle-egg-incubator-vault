"""
=============================================================================
Module:     utils/session.py
Project:    Incubator Vault v7.2.0 — Wildlife In Need Center (WINC)
Purpose:    Session management, SessionID generation, and Splash Screen Gate.
=============================================================================
"""

import streamlit as st
import uuid
from datetime import datetime
from utils.db import get_supabase
from utils.logger import logger

def init_session():
    """Initializes the browser session state for v7.2.0 requirements.
    
    Generates a unique SessionID for auditing and manages the 
    Restorative Hydration Gate status.
    """
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"🆕 New Vault Session Initialized: {st.session_state.session_id}")

    if 'observer_id' not in st.session_state:
        st.session_state.observer_id = None
        
    if 'observer_name' not in st.session_state:
        st.session_state.observer_name = "Guest"

    # §1.8 Restorative Hydration Gate (v7.2.0 requirement)
    if 'env_gate_synced' not in st.session_state:
        st.session_state.env_gate_synced = False

def show_splash_screen():
    st.markdown("<div style='text-align: center; padding: 50px;'><h1 style='color: #10B981;'>🐢 WINC Incubator Vault</h1><p style='color: #94A3B8;'>Please select your name to begin the session</p></div>", unsafe_allow_html=True)
    supabase = get_supabase()
    
    # Requirement §1.6: Fetch active observers for the gate
    try:
        observers = supabase.table('observer').select('*').eq('is_active', True).execute().data
        if not observers:
            st.error("No active observers found in registry.")
            st.stop()
            
        cols = st.columns([1, 2, 1])
        with cols[1]:
            with st.form("login_form"):
                options = {f"{o['display_name']} ({o['role']})": o['id'] for o in observers}
                selected = st.selectbox("Observer Identity", options=list(options.keys()))
                if st.form_submit_button("Launch Vault", width='stretch'):
                    st.session_state.observer_id = options[selected]
                    st.session_state.observer_name = selected.split(' (')[0]
                    
                    # 🚨 TELEMETRY: Record Access Log so the Settings Audit page isn't totally empty
                    try:
                        supabase.table('systemlog').insert({
                            "session_id": st.session_state.get('session_id', 'UNKNOWN'),
                            "event_type": "ACCESS",
                            "event_message": f"Biologist {st.session_state.observer_name} clocked in."
                        }).execute()
                    except:
                        pass
                        
                    st.rerun()
    except Exception as e:
        st.error(f"Vault Connection Failure: {e}")

def render_custom_sidebar():
    """Displays observer info at the top of the sidebar with SessionID."""
    st.sidebar.markdown(f"### 👤 {st.session_state.get('observer_name', 'User')}")
    st.sidebar.caption(f"SessionID: {st.session_state.get('session_id', 'Unknown')}")
    if st.sidebar.button("Log Out", key="global_logout_btn", width='stretch'): 
        st.session_state.observer_id = None
        st.session_state.env_gate_synced = False
        st.rerun()
    st.sidebar.divider()
