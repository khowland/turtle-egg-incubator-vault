from utils.session import render_custom_sidebar
render_custom_sidebar()
"""
=============================================================================
Module:     src/2_🐣_New_Intake.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    4-Step High-Efficiency Intake Wizard for salvaging turtle eggs.
            Optimized for field use with wet/gloved hands.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06
=============================================================================
"""

import streamlit as st
from datetime import date
from utils.session import render_custom_sidebar
from utils.css import BASE_CSS
from utils.db import get_supabase
from utils.logger import logger

st.set_page_config(page_title="New Intake | WINC", page_icon="🐣", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_custom_sidebar()

# --- SESSION STATE INITIALIZATION ---
if 'intake_step' not in st.session_state: st.session_state.intake_step = 1
if 'intake_data' not in st.session_state: st.session_state.intake_data = {}

def next_step(): st.session_state.intake_step += 1
def prev_step(): st.session_state.intake_step -= 1
def reset_intake(): 
    st.session_state.intake_step = 1
    st.session_state.intake_data = {}
    st.rerun()

# --- TITLE & PROGRESS ---
st.title("🐣 New Intake Wizard")
st.progress(st.session_state.intake_step / 4, text=f"Step {st.session_state.intake_step} of 4")

# --- STEP 1: MOTHER IDENTITY ---
if st.session_state.intake_step == 1:
    st.markdown("### 🐢 Step 1: Mother Identity")
    with st.container(border=True):
        species_list = ["Blanding's Turtle", "Wood Turtle", "Ornate Box Turtle", "Snapping Turtle", "Painted Turtle"]
        species = st.selectbox("Species", options=species_list, index=0)
        mother_name = st.text_input("Mother Name (e.g. Shelly)", placeholder="Shelly")
        condition = st.radio("Mother Condition", options=["Healthy/Living", "Injured", "DOA (Salvage)", "Post-Mortem Harvest"], horizontal=True)
        intake_date = st.date_input("Intake Date", value=date.today())
        
        st.markdown("**Location Data**")
        col1, col2 = st.columns([2, 1])
        location = col1.text_input("Harvest Location Description", placeholder="Hwy 12 & Cty P")
        if col2.button("📍 Capture GPS", use_container_width=True):
            st.toast("GPS Coordinates Captured (Simulated)")
            st.session_state.intake_data['gps'] = "43.0731° N, 89.4012° W"
            
        if st.button("Next Step ➡️", use_container_width=True):
            if not mother_name:
                st.error("Mother Name is required for Clue-Chain generation.")
            else:
                st.session_state.intake_data.update({
                    'species': species, 'mother_name': mother_name, 
                    'condition': condition, 'intake_date': str(intake_date), 'location': location
                })
                next_step()
                st.rerun()

# --- STEP 2: BIN SETUP ---
elif st.session_state.intake_step == 2:
    st.markdown("### 📦 Step 2: Bin Setup")
    with st.container(border=True):
        harvest_date = st.date_input("Harvest/Lay Date", value=date.today())
        substrate = st.selectbox("Substrate", options=["Vermiculite (1:1)", "Perlite", "Peat Mix", "Soil/Sand Blend"])
        bin_label = st.text_input("Physical Bin Label (Optional)", placeholder="Bin-A1")
        
        st.info(f"Estimated Hatch Window: **Aug 15 - Aug 30** (Based on {st.session_state.intake_data['species']})")
        
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Back", use_container_width=True): prev_step(); st.rerun()
        if col2.button("Next Step ➡️", use_container_width=True):
            st.session_state.intake_data.update({'harvest_date': str(harvest_date), 'substrate': substrate, 'bin_label': bin_label})
            next_step()
            st.rerun()

# --- STEP 3: EGG BURST ---
elif st.session_state.intake_step == 3:
    st.markdown("### 🥚 Step 3: Egg Quantity")
    with st.container(border=True):
        egg_count = st.number_input("Total Eggs Harvested", min_value=1, max_value=100, value=12)
        marking = st.text_input("Egg Marking Pattern (Applied to all)", placeholder="Red Dot / Numbered")
        
        st.success(f"System will generate IDs: **{st.session_state.intake_data['mother_name']}_E01** through **E{egg_count:02}**")
        
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Back", use_container_width=True): prev_step(); st.rerun()
        if col2.button("Next Step ➡️", use_container_width=True):
            st.session_state.intake_data.update({'egg_count': egg_count, 'marking': marking})
            next_step()
            st.rerun()

# --- STEP 4: REVIEW & COMMIT ---
elif st.session_state.intake_step == 4:
    st.markdown("### ✅ Step 4: Final Review")
    data = st.session_state.intake_data
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Mother:** {data['mother_name']} ({data['species']})")
        st.markdown(f"**Condition:** {data['condition']}")
        st.markdown(f"**Location:** {data['location']}")
    with col2:
        st.markdown(f"**Bin:** {data['bin_label']} ({data['substrate']})")
        st.markdown(f"**Eggs:** {data['egg_count']} eggs with marking '{data['marking']}'")
        
    st.warning("⚠️ Once committed, IDs will be generated and biological clocks will start.")
    
    col1, col2 = st.columns([1, 2])
    if col1.button("⬅️ Back", use_container_width=True): prev_step(); st.rerun()
    if col2.button("🚀 COMMIT TO VAULT", use_container_width=True):
        st.balloons()
        st.success("Hatchery records created successfully! (Database sync simulated)")
        if st.button("Start New Intake", use_container_width=True): reset_intake()
