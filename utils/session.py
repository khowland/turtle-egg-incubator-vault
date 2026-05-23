"""
=============================================================================
Module:        utils/session.py
Project:       Incubator Vault v8.0.0
Requirement:   Matches Standard [§35, §36]
Description:   Session management and Forensic Recovery.
=============================================================================
"""

import streamlit as st
import uuid
import os
from datetime import datetime, timedelta, timezone
from utils.db import get_supabase
from utils.bootstrap import get_resilient_table, get_app_version
from utils.logger import logger, log_exceptions

@log_exceptions
def init_session():
    """Initializes the browser session state."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        logger.info(f"🆕 New System Session Initialized: {st.session_state.session_id}")

    # 🛡️ GLOBAL QA BYPASS: Handled in app.py, but safe-guarded here
    if "observer_id" not in st.session_state:
        st.session_state.observer_id = None

    if "observer_name" not in st.session_state:
        st.session_state.observer_name = "Guest"

    if "env_gate_synced" not in st.session_state:
        st.session_state.env_gate_synced = {}

@st.cache_data(ttl=600)
@log_exceptions
def fetch_active_observers():
    """Fetches the list of active observers from Supabase."""
    try:
        supabase_client = get_supabase()
        response = (
            supabase_client.table("observer")
            .select("observer_id, observer_name, is_active")
            .eq("is_active", True)
            .execute()
        )
        return response.data
    except Exception as e:
        logger.error(f"Failed to fetch observers: {e}")
        return []

@log_exceptions
def is_session_adoptable(last_login_iso: str) -> bool:
    """Standard §36: Forensic Session Recovery."""
    try:
        last_timestamp = datetime.fromisoformat(last_login_iso.replace("Z", "+00:00"))
        diff = datetime.now(timezone.utc) - last_timestamp
        return diff <= timedelta(hours=1)
    except Exception:
        return False

def show_splash_screen():
    supabase_client = get_supabase()
    st.markdown("<div style='text-align: center; padding: 6vh 2rem 1rem 2rem; max-width: 480px; margin: 0 auto;'>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <h1 style='color: #10B981; margin-bottom: 0.4rem;'>🐢 Welcome!</h1>
            <p style='color: #94A3B8; margin: 0.2rem 0;'>Let's get started. Who is working today?</p>
            <p style='color: #94a3b8; font-size: 0.78em; margin-top: 0.6rem; letter-spacing: 0.04em;'>Version {get_app_version()}</p>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    active_observers = fetch_active_observers()
    if not active_observers:
        st.error("No active observers found in registry or connection failed.")
        st.stop()

    try:
        columns = st.columns([1, 2, 1])
        with columns[1]:
            with st.form("login_form"):
                observer_options = {f"{o['observer_name']}": o["observer_id"] for o in active_observers}
                names_list = list(observer_options.keys())
                selected_observer = st.selectbox("Select Your Name", options=names_list)

                if st.form_submit_button("START", use_container_width=True, key="login_start"):
                    st.session_state.observer_id = observer_options[selected_observer]
                    st.session_state.observer_name = selected_observer.split(" (")[0]
                    st.rerun()
    except Exception as error:
        st.error(f"Vault Connection Failure: {error}")
