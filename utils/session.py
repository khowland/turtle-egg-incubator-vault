"""
=============================================================================
Module:     utils/session.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    Manages observer identity, session persistence, and sidebar UI.
=============================================================================
"""

import streamlit as st
from utils.db import get_supabase

def init_session():
    """Initialize standard session state variables."""
    if 'session_id' not in st.session_state: st.session_state.session_id = None
    if 'observer_id' not in st.session_state: st.session_state.observer_id = None
    if 'env_synced' not in st.session_state: st.session_state.env_synced = False

def show_splash_screen():
    """Display a clean login/splash screen for user selection."""
    st.markdown("<div style='text-align: center; padding: 50px;'><h1 style='color: #10B981;'>🐢 WINC Incubator Vault</h1><p style='color: #94A3B8;'>Please select your name to begin the session</p></div>", unsafe_allow_html=True)
    supabase = get_supabase()
    observers = supabase.table('observer').select('*').eq('is_active', True).execute().data
    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.form("login_form"):
            options = {f"{o['display_name']} ({o['role']})": o['id'] for o in observers}
            selected = st.selectbox("Observer Identity", options=list(options.keys()))
            if st.form_submit_button("Launch Vault", use_container_width=True):
                st.session_state.observer_id = options[selected]
                st.session_state.observer_name = selected.split(' (')[0]
                st.rerun()

def render_custom_sidebar():
    """Render the global sidebar with branding and observer info."""
    with st.sidebar:
        
        st.info(f"👤 **Observer:** {st.session_state.get('observer_name', 'None')}")
        if st.button("Log Out / Change User"):
            st.session_state.observer_id = None
            st.rerun()
        st.divider()
        st.markdown("<div style='text-align: center; color: #64748B; font-size: 0.8rem;'>BUILD: v6.3.2 — WINC EDITION</div>", unsafe_allow_html=True)
