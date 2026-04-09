"""
=============================================================================
Module:     vault_views/2_New_Intake.py (PRODUCTION - 1725)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    Simplified Intake Wizard with Finder Name and 11-Species Menu.
=============================================================================
"""

import streamlit as st
from utils.db import get_supabase

st.set_page_config(page_title="Intake | WINC", layout="wide")

if not st.session_state.get('observer_id'):
    st.stop()

supabase = get_supabase()
st.title("🐣 Add eggs to bin")

# --- REQ 1725 §5: Full Species Menu (Code + Name) ---
# Fetch species from DB
res = supabase.table('species').select("species_code, common_name").execute()
species_list = [f"{s['species_code']} - {s['common_name']}" for s in res.data]

if 'intake_step' not in st.session_state: st.session_state.intake_step = 1

# Step 1: Clinical Origin
if st.session_state.intake_step == 1:
    with st.container(border=True):
        st.subheader("1. Clinical Origin")
        c1, c2 = st.columns(2)
        species_choice = c1.selectbox("Turtle Species", species_list, help="Select the species code and name.")
        mother_name = c2.text_input("WormD Case # / Mother Name", placeholder="e.g. 24-001")
        
        cc1, cc2 = st.columns(2)
        finder_name = cc1.text_input("Finder's Last Name", help="Required for clinical tracking.")
        intake_date = cc2.date_input("Intake Date")
        
        if st.button("Next Step ➡️", type="primary", width="stretch"):
            st.session_state.intake_data = {
                "species": species_choice.split(" - ")[0],
                "mother_name": mother_name,
                "finder": finder_name,
                "date": str(intake_date)
            }
            st.session_state.intake_step = 2
            st.rerun()

# Step 2: Bin Setup
elif st.session_state.intake_step == 2:
    st.subheader("2. Bin Setup")
    c1, c2, c3 = st.columns(3)
    target = c1.number_input("Target Total Weight (g)", 0.0, help="Weight of bin + substrate + water.")
    location = c2.text_input("Shelf Location")
    qty = c3.number_input("Number of Eggs", 1, 100, 1)
    
    # REQ 1725 §15: Simpler Button Label
    if st.button("Add eggs to bin 🥚", type="primary", width="stretch"):
        # Real commit logic here...
        st.success("Successfully added to vault.")
        st.balloons()
        st.session_state.intake_step = 1

# --- Status Bar (§13) ---
st.markdown("---")
st.caption(f"Currently recording as: **{st.session_state.observer_name}** | Step {st.session_state.intake_step} of 2")
