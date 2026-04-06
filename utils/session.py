"""
=============================================================================
Module:     utils/session.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Session management, observer identity tracking, and persistent
            sidebar UI rendering.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
import requests
from datetime import datetime
from streamlit_lottie import st_lottie
from utils.db import get_supabase_client

# =============================================================================
# SECTION: Session Initialization
# =============================================================================

def init_session(observer_id: str, display_name: str):
    """Generates a new session ID and stores observer state.
    
    Args:
        observer_id: Slug for the observer.
        display_name: Full name for UI.
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    session_id = f"{observer_id}_{timestamp}"
    st.session_state["session_id"] = session_id
    st.session_state["observer_id"] = observer_id
    st.session_state["observer_name"] = display_name
    st.session_state["logged_in"] = True

def get_active_session():
    return st.session_state.get("session_id")

# =============================================================================
# SECTION: Persistent Sidebar UI
# =============================================================================

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def render_sidebar():
    """Renders the consistent sidebar elements according to §4 wireframe."""
    with st.sidebar:
        st.markdown("## 🐢 VAULT ELITE PRO")
        st.markdown("`BUILD: v6.0 — TITANIUM`", unsafe_allow_html=True)
        
        # Lottie Animation
        lottie_url = "https://assets5.lottiefiles.com/packages/lf20_t9gk8kb4.json"
        lottie_json = load_lottieurl(lottie_url)
        if lottie_json:
            st_lottie(lottie_json, height=120, key="sidebar_turtle")
            
        st.markdown("--- observer selection ---")
        
        # Observer Selection
        supabase = get_supabase_client()
        observers = []
        try:
            res = supabase.table("observer").select("*").eq("is_active", True).execute()
            observers = res.data
        except:
            # Fallback for early build stages
            observers = [
                {"observer_id": "elisa", "display_name": "Elisa Rodriguez"},
                {"observer_id": "kevin", "display_name": "Kevin Howland"}
            ]
            
        obs_names = [o["display_name"] for o in observers]
        current_name = st.session_state.get("observer_name")
        
        selected_name = st.selectbox(
            "👤 Current Observer",
            options=["-- Select --"] + obs_names,
            index=obs_names.index(current_name) + 1 if current_name in obs_names else 0
        )
        
        if selected_name != "-- Select --":
            selected_id = next(o["observer_id"] for o in observers if o["display_name"] == selected_name)
            if st.session_state.get("observer_id") != selected_id:
                init_session(selected_id, selected_name)
                st.rerun()
        else:
            st.session_state["logged_in"] = False
            st.warning("⚠️ Select observer to enable entry.")

        st.markdown("--- navigation ---")
        # Streamlit handles pages/ automatically below this
        
        if st.button("🔄 NEURAL REFRESH"):
            st.cache_resource.clear()
            st.rerun()
            
        sid = get_active_session()
        if sid: st.caption(f"ID: {sid}")
