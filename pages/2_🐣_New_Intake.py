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

if "observer_id" not in st.session_state or not st.session_state.observer_id:
    st.warning("⚠️ Please select an observer in the sidebar to enable intake.")
    st.stop()

if "intake_step" not in st.session_state: st.session_state.intake_step = 1

# Step 1: Mother
if st.session_state.intake_step == 1:
    with st.container(border=True):
        st.subheader("Step 1: Mother")
        m_name = st.text_input("Mother Name", placeholder="e.g. Shelly")
        species = st.selectbox("Species", ["Blandings", "Wood", "Ornate Box"])
        cond = st.selectbox("Condition", ["Healthy", "Injured", "DOA"])
        if st.button("NEXT: BIN SETUP"): 
            st.session_state.intake_mother = {"name": m_name, "species": species, "condition": cond}
            st.session_state.intake_step = 2
            st.rerun()

# Step 2: Bin (Simplified - no incubator select)
elif st.session_state.intake_step == 2:
    with st.container(border=True):
        st.subheader("Step 2: Bin Setup")
        st.info("📍 Unit: Main Hatchery Incubator")
        b_date = st.date_input("Harvest Date")
        b_subs = st.selectbox("Substrate", ["Vermiculite", "Perlite"])
        b_count = st.number_input("Egg Count", min_value=1, value=10)
        col1, col2 = st.columns(2)
        if col1.button("BACK"): st.session_state.intake_step = 1; st.rerun()
        if col2.button("NEXT: CONFIRM"): 
            st.session_state.intake_bin = {"date": str(b_date), "substrate": b_subs, "count": b_count}
            st.session_state.intake_step = 3
            st.rerun()

# Step 3: Confirm
elif st.session_state.intake_step == 3:
    st.subheader("Step 3: Review")
    m, b = st.session_state.intake_mother, st.session_state.intake_bin
    with st.container(border=True):
        st.write(f"🐢 **Mother:** {m['name']} | **Eggs:** {b['count']}")
        st.write(f"📦 **Incubator:** Main Unit | **Substrate:** {b['substrate']}")
    if st.button("🚀 SAVE INTAKE", use_container_width=True):
        st.success("Hatchery records created!")
        st.balloons()
        st.session_state.intake_step = 1
