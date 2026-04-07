"""
=============================================================================
Module:     pages/4_🌡️_Temp_Humidity.py
Project:    Incubator Vault v6.2 — Wildlife In Need Center (WINC)
Purpose:    Environment telemetry logging for the main incubator.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""
import streamlit as st
import pandas as pd
from utils.db import get_supabase_client
from utils.audit import logged_write

st.set_page_config(page_title="Environment Log", layout="centered")
st.title("🌡️ Environment Log")

supabase = get_supabase_client()

if "observer_id" not in st.session_state or not st.session_state.observer_id:
    st.warning("⚠️ Please select an observer in the sidebar to log data.")
    st.stop()

with st.container(border=True):
    st.subheader("Quick Log")
    st.info("📍 Unit: Main Hatchery Incubator")
    
    col1, col2 = st.columns(2)
    with col1:
        temp = st.number_input("Temperature (°F)", value=82.0, step=0.1, format="%.1f")
    with col2:
        hum = st.number_input("Humidity (%)", value=80, step=1)
    
    notes = st.text_area("Notes")
    
    if st.button("💾 LOG ENVIRONMENT READING", use_container_width=True):
        def save_reading():
            return supabase.table("systemlog").insert({
                "session_id": st.session_state.session_id,
                "event_type": "ENV_LOG",
                "event_message": "Environment check logged",
                "payload": {"temp": temp, "humidity": hum, "notes": notes}
            }).execute()
            
        logged_write(supabase, st.session_state.session_id, "ENV_LOG", {"temp": temp, "hum": hum}, save_reading)
        st.success("Reading logged successfully!")
        st.rerun()

st.subheader("Recent Readings")
hist = supabase.table("systemlog").select("*").eq("event_type", "ENV_LOG").order("timestamp", desc=True).limit(10).execute()
if hist.data:
    df = pd.DataFrame([{"Time": r['timestamp'], "Temp": r['payload']['temp'], "Hum": r['payload']['humidity'], "Notes": r['payload'].get('notes', '')} for r in hist.data])
    st.dataframe(df, hide_index=True, use_container_width=True)
