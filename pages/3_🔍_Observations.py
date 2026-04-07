"""
=============================================================================
Module:     pages/3_🔍_Observations.py
Project:    WINC Incubator Vault v6.3
Purpose:    Batch observation logging for eggs. Includes a one-time 
            environment sync (Temp/Humidity) per session.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06
=============================================================================
"""

import streamlit as st
from utils.session import render_sidebar
from utils.css import BASE_CSS
from utils.db import get_supabase
from utils.audit import logged_write

st.set_page_config(page_title="Observations | WINC", page_icon="🔍", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_sidebar()

st.title("🔍 Observations")

# --- ENVIRONMENT GATE (Once per session) ---
if not st.session_state.get('env_synced'):
    with st.expander("🌡️ STEP 1: Sync Incubator Environment", expanded=True):
        st.warning("Before logging observations, please record the current incubator status.")
        with st.form("env_sync_form"):
            col1, col2 = st.columns(2)
            temp = col1.number_input("Incubator Temp (°F)", min_value=60.0, max_value=110.0, value=82.0, step=0.1)
            hum = col2.number_input("Incubator Humidity (%)", min_value=0.0, max_value=100.0, value=80.0, step=1.0)
            notes = st.text_area("Environment Notes (Optional)")
            
            if st.form_submit_button("Save & Unlock Observations", use_container_width=True):
                # Record the environment observation
                st.session_state.env_synced = True
                st.session_state.current_temp = temp
                st.session_state.current_hum = hum
                st.success("Environment synced! You can now log egg health.")
                st.rerun()
    st.stop()

# --- MAIN OBSERVATION UI (Unlocked) ---
st.markdown(f"**Current Session:** {st.session_state.current_temp}°F / {st.session_state.current_hum}% Humidity")
if st.button("📝 Edit Environment Metrics"):
    st.session_state.env_synced = False
    st.rerun()

st.divider()
st.info("🚧 Multi-select egg grid and batch logging coming in next sub-update.")
