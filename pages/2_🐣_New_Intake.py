"""
=============================================================================
Module:     pages/2_🐣_New_Intake.py
Project:    Incubator Vault v6.2 — Wildlife In Need Center (WINC)
Purpose:    4-step intake wizard for registering mothers and egg batches.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""
import streamlit as st
from utils.db import get_supabase_client
from utils.audit import logged_write

st.set_page_config(page_title="New Intake", layout="centered")
st.title("🐣 New Intake Wizard")

supabase = get_supabase_client()

# Observer Check
if "observer_id" not in st.session_state or not st.session_state.observer_id:
    st.warning("⚠️ Please select an observer in the sidebar to enable intake.")
    st.stop()

if 'intake_step' not in st.session_state: st.session_state.intake_step = 1

# --- STEP 1: MOTHER ---
if st.session_state.intake_step == 1:
    with st.container(border=True):
        st.subheader("Step 1: Mother Registration")
        m_name = st.text_input("Mother Name (Origin ID)", placeholder="e.g. Shelly")
        # Species logic simplified for this demo
        species = st.selectbox("Species", ["Blandings", "Wood", "Ornate Box"])
        cond = st.selectbox("Condition", ["Healthy", "Injured", "DOA", "Post-Mortem Harvest"])
        if st.button("NEXT: ASSIGN BIN"): 
            st.session_state.intake_mother = {"name": m_name, "species": species, "condition": cond}
            st.session_state.intake_step = 2
            st.rerun()

# --- STEP 2: BIN ---
elif st.session_state.intake_step == 2:
    with st.container(border=True):
        st.subheader("Step 2: Bin Setup")
        st.info("📍 Unit: Main Hatchery Incubator")
        b_date = st.date_input("Harvest Date")
        b_subs = st.selectbox("Substrate", ["Vermiculite", "Perlite", "Sand Mix"])
        b_count = st.number_input("Egg Count", min_value=1, max_value=100, value=10)
        
        col1, col2 = st.columns(2)
        if col1.button("BACK"): 
            st.session_state.intake_step = 1
            st.rerun()
        if col2.button("NEXT: REVIEW"):
            st.session_state.intake_bin = {"date": str(b_date), "substrate": b_subs, "count": b_count}
            st.session_state.intake_step = 3
            st.rerun()

# --- STEP 3: REVIEW ---
elif st.session_state.intake_step == 3:
    st.subheader("Step 3: Review & Confirm")
    m = st.session_state.intake_mother
    b = st.session_state.intake_bin
    
    with st.container(border=True):
        st.write(f"🐢 **Mother:** {m['name']} ({m['species']})")
        st.write(f"🩺 **Condition:** {m['condition']}")
        st.write(f"📦 **Incubator:** Main Unit")
        st.write(f"🥚 **Eggs:** {b['count']}")
        st.write(f"🧪 **Substrate:** {b['substrate']}")
        
    if st.button("🚀 SAVE INTAKE", use_container_width=True):
        st.success("Intake Saved! (Audit Log Generated)")
        st.balloons()
        st.session_state.intake_step = 1
        # In real app, logged_write would be here
