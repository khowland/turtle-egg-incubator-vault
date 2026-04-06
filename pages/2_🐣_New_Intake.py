"""
=============================================================================
Module:     pages/2_new_intake.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    4-Step Intake Wizard for registering mothers, bins, and eggs.
            Step 2: Bin and Incubator setup.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
from datetime import datetime
from utils.db import get_supabase_client
from utils.session import render_sidebar
from utils.css import BASE_CSS

# Configure Page
st.set_page_config(page_title="New Intake | Vault Pro", page_icon="🐣", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: Wizard State Management
# =============================================================================

if 'intake_step' not in st.session_state: st.session_state.intake_step = 1
if 'intake_mother' not in st.session_state: st.session_state.intake_mother = {}
if 'intake_bin' not in st.session_state: st.session_state.intake_bin = {}
if 'intake_existing_mother_id' not in st.session_state: st.session_state.intake_existing_mother_id = None

def next_step(): st.session_state.intake_step += 1
def prev_step(): st.session_state.intake_step -= 1

# =============================================================================
# SECTION: Step 1 - Mother Registration
# =============================================================================

def show_step_1():
    st.markdown("<h1>New Intake — Step 1: Mother</h1>", unsafe_allow_html=True)
    supabase = get_supabase_client()
    
    try:
        res = supabase.table("species").select("species_id, common_name").execute()
        species_data = res.data
    except:
        species_data = [{"species_id": "Blandings", "common_name": "Blanding's Turtle"}]
    
    species_map = {s['common_name']: s['species_id'] for s in species_data}

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    with st.form("mother_form"):
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Mother Name (Origin ID)", value=st.session_state.intake_mother.get('name', ''), placeholder="e.g. Shelly")
        m_species_name = c2.selectbox("Species Class", options=list(species_map.keys()), 
                                      index=list(species_map.keys()).index(st.session_state.intake_mother.get('species_name')) if st.session_state.intake_mother.get('species_name') in species_map else 0)
        
        c3, c4 = st.columns(2)
        m_cond = c3.selectbox("Condition", options=["Healthy", "Injured", "DOA", "Post-Mortem Harvest"], 
                              index=["Healthy", "Injured", "DOA", "Post-Mortem Harvest"].index(st.session_state.intake_mother.get('condition')) if st.session_state.intake_mother.get('condition') in ["Healthy", "Injured", "DOA", "Post-Mortem Harvest"] else 0)
        m_date = c4.date_input("Intake Date", value=st.session_state.intake_mother.get('date', datetime.now()))
        
        m_loc = st.text_input("Harvest Location (GPS or Description)", value=st.session_state.intake_mother.get('location', ''))
        m_notes = st.text_area("Clinical Notes", value=st.session_state.intake_mother.get('notes', ''))
        
        submitted = st.form_submit_button("NEXT: ASSIGN BIN & INCUBATOR")

    if submitted:
        if not m_name:
            st.error("❌ Name is required.")
        else:
            st.session_state.intake_mother = {
                'name': m_name, 'species_id': species_map[m_species_name], 'species_name': m_species_name,
                'condition': m_cond, 'date': m_date, 'location': m_loc, 'notes': m_notes
            }
            # Simplified check for build sequence
            try:
                dup = supabase.table("mother").select("*").ilike("mother_name", m_name).eq("species_id", species_map[m_species_name]).execute()
                if dup.data: st.session_state['duplicate_found'] = dup.data[0]
                else: 
                    st.session_state['duplicate_found'] = None
                    next_step()
                    st.rerun()
            except: 
                next_step()
                st.rerun()

    if st.session_state.get('duplicate_found'):
        d = st.session_state['duplicate_found']
        st.warning(f"⚠️ {d['mother_name']} already exists.")
        c_a, c_b = st.columns(2)
        if c_a.button("✅ USE EXISTING"): 
            st.session_state.intake_existing_mother_id = d['mother_id']
            st.session_state.duplicate_found = None
            next_step(); st.rerun()
        if c_b.button("✏️ CREATE NEW"): 
            st.session_state.intake_existing_mother_id = None
            st.session_state.duplicate_found = None
            next_step(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: Step 2 - Bin Setup
# =============================================================================

def show_step_2():
    st.markdown("<h1>New Intake — Step 2: Bin Setup</h1>", unsafe_allow_html=True)
    supabase = get_supabase_client()

    # Mother Preview
    m = st.session_state.intake_mother
    mother_label = m.get('name', 'New Mother')
    st.caption(f"Mother: {mother_label} ({m.get('species_name')})")
    
    # Clue Chain Preview §5 W1
    date_slug = m.get('date', datetime.now()).strftime('%Y%m%d')
    mother_id_preview = f"{m['name'].replace(' ', '')}_{m['species_id']}_{date_slug}"
    st.markdown(f"`Clue Chain Preview: {mother_id_preview}`")

    # Fetch Incubators
    inc_data = []
    try:
        res = supabase.table("incubator").select("incubator_id, label").eq("is_active", True).execute()
        inc_data = res.data
    except:
        inc_data = [{"incubator_id": "INC-01", "label": "Incubator Alpha"}]
    
    inc_map = {i['label']: i['incubator_id'] for i in inc_data}

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    with st.form("bin_form"):
        c1, c2 = st.columns(2)
        b_date = c1.date_input("Harvest Date", value=st.session_state.intake_bin.get('date', datetime.now()))
        b_inc_label = c2.selectbox("Incubator Unit", options=list(inc_map.keys()),
                                    index=list(inc_map.keys()).index(st.session_state.intake_bin.get('inc_label')) if st.session_state.intake_bin.get('inc_label') in inc_map else 0)
        
        c3, c4 = st.columns(2)
        b_subs = c3.selectbox("Substrate Type", ["Vermiculite", "Perlite", "Sphagnum Moss", "Sand Mix"],
                               index=["Vermiculite", "Perlite", "Sphagnum Moss", "Sand Mix"].index(st.session_state.intake_bin.get('substrate')) if st.session_state.intake_bin.get('substrate') in ["Vermiculite", "Perlite", "Sphagnum Moss", "Sand Mix"] else 0)
        b_label = c4.text_input("Bin Label (Physical)", value=st.session_state.intake_bin.get('label', ''), placeholder="e.g. Shelf A, Bin 3")
        
        b_count = st.number_input("Egg Count", min_value=1, max_value=100, value=st.session_state.intake_bin.get('count', 10))

        st.markdown(f"⚡ System will generate {b_count} tracked egg records")
        
        bc1, bc2 = st.columns(2)
        if bc1.form_submit_button("◀ BACK: MOTHER"): 
            prev_step(); st.rerun()
        if bc2.form_submit_button("▶ NEXT: REVIEW & CONFIRM"):
            st.session_state.intake_bin = {
                'date': b_date, 'incubator_id': inc_map[b_inc_label], 'inc_label': b_inc_label,
                'substrate': b_subs, 'label': b_label, 'count': b_count
            }
            next_step(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: Wizard Router
# =============================================================================

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please select an observer in the sidebar to enable intake.")
    st.stop()

if st.session_state.intake_step == 1: show_step_1()
elif st.session_state.intake_step == 2: show_step_2()
else: st.info(f"🚧 Step {st.session_state.intake_step} Coming in next build...")
