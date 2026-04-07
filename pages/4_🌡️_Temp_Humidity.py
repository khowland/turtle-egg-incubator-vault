"""
=============================================================================
Module:     pages/4_temp_humidity.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Environment telemetry logging for tracking incubator temp/humidity.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db import get_supabase_client
from utils.session import render_sidebar
from utils.css import BASE_CSS
from utils.audit import logged_write
from utils.logger import logger

# Configure Page
st.set_page_config(page_title="Temp & Humidity | Incubator Vault", page_icon="🌡️", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: UI Components
# =============================================================================

st.markdown("## 🌡️ Temp & Humidity")

if not st.session_state.get("logged_in"):
    st.warning("⬆️ Pick your name in the sidebar first.")
    st.stop()

supabase = get_supabase_client()

# --- LOGGING FORM ---
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("### 📝 Log New Reading")

# Fetch Incubators for Dropdown
try:
    inc_res = supabase.table("incubator").select("incubator_id, label, target_temp, target_humidity").eq("is_active", True).execute()
    incubators = inc_res.data
except Exception as e:
    # Fallback if incubator table doesn't exist yet
    logger.warning(f"Incubator query failed, using fallback: {e}")
    incubators = [{"incubator_id": "INC-01", "label": "Incubator Alpha", "target_temp": 82.0, "target_humidity": 80.0}]

inc_map = {i['label']: i for i in incubators}

with st.form("env_form"):
    c1, c2, c3 = st.columns(3)
    
    sel_inc_label = c1.selectbox("Incubator Unit", options=list(inc_map.keys()))
    target = inc_map[sel_inc_label]
    
    temp = c2.number_input("Temperature (°F)", min_value=60.0, max_value=110.0, value=float(target['target_temp'] or 82.0), step=0.1)
    hum = c3.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=float(target['target_humidity'] or 80.0), step=1.0)
    
    notes = st.text_area("Observations / Maintenance Notes", placeholder="e.g. Water reservoir refilled.")
    
    if st.form_submit_button("💾 Save Reading"):
        def save_reading():
            payload = {
                "incubator_id": target['incubator_id'],
                "ambient_temp": temp,
                "humidity": hum,
                "notes": notes,
                "observer_id": st.session_state.observer_id,
                "session_id": st.session_state.session_id
            }
            # Requirement: Insert into IncubatorObservation table
            supabase.table("IncubatorObservation").insert(payload).execute()
            return True

        try:
            logged_write(supabase, st.session_state.session_id, "ENV_LOG", 
                         {"incubator_id": target['incubator_id'], "temp": temp, "hum": hum}, save_reading)
            st.success(f"✅ Telemetry saved for {sel_inc_label}.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# --- RECENT READINGS ---
st.markdown("### 📊 Recent Readings (Last 24h)")
try:
    # Join with observer to show who logged it
    readings_res = supabase.table("IncubatorObservation")\
        .select("*, incubator:incubator_id(label), observer:observer_id(display_name)")\
        .order("timestamp", desc=True).limit(20).execute()
    
    if readings_res.data:
        df = pd.DataFrame(readings_res.data)
        # Flatten for display
        df['Unit'] = df['incubator'].apply(lambda x: x['label'] if x else 'Unknown')
        df['Observer'] = df['observer'].apply(lambda x: x['display_name'] if x else 'Unknown')
        df['Time'] = pd.to_datetime(df['timestamp']).dt.strftime('%m/%d %I:%M %p')
        
        st.dataframe(df[['Time', 'Unit', 'ambient_temp', 'humidity', 'Observer', 'notes']], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("No telemetry data logged in the last 24 hours.")
except Exception as e:
    st.error(f"⚠️ Could not load recent readings: {e}")
