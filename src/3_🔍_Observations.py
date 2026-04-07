"""
=============================================================================
Module:     src/3_🔍_Observations.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    Environment Gate and Multi-Select Observation Grid.
=============================================================================
"""
import streamlit as st
from utils.session import render_custom_sidebar
from utils.css import BASE_CSS
from utils.db import get_supabase

st.set_page_config(page_title="Observations | WINC", page_icon="🔍", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_custom_sidebar()

st.title("🔍 Observation Engine")

# --- ENVIRONMENT GATE LOGIC ---
if 'env_synced' not in st.session_state:
    st.session_state.env_synced = False

if not st.session_state.env_synced:
    st.markdown("### 🌡️ Environment Check-In Required")
    with st.container(border=True):
        st.info("Please record current incubator metrics before proceeding with observations.")
        temp = st.number_input("Incubator Temp (°F)", min_value=70.0, max_value=100.0, value=84.5)
        humidity = st.number_input("Incubator Humidity (%)", min_value=10.0, max_value=100.0, value=80.0)
        
        if st.button("✅ Sync & Unlock Grid", use_container_width=True):
            st.session_state.env_synced = True
            st.session_state.current_temp = temp
            st.session_state.current_humidity = humidity
            st.success("Environment Synced! (Session ID Generated)")
            st.rerun()
else:
    st.success(f"✅ Session Active | Temp: {st.session_state.current_temp}°F | Humidity: {st.session_state.current_humidity}%")
    if st.button("📝 Edit Environment Metrics"): 
        st.session_state.env_synced = False
        st.rerun()

    st.divider()
    st.markdown("### 🥚 Multi-Select Egg Grid")
    st.info("Choose eggs from the vault to log health flags, chalking, or vascularity.")
    # (Placeholder for multi-select grid logic)
    st.write("Select Species → Select Bin → Bulk Log Observations")
