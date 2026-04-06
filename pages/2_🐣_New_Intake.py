"""
=============================================================================
Module:     pages/2_new_intake.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    4-Step Intake Wizard for registering mothers, bins, and eggs.
            Steps 1-4: Mother, Bin, Egg Generation, and Atomic Save.
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
def reset_wizard():
    st.session_state.intake_step = 1
    st.session_state.intake_mother = {}
    st.session_state.intake_bin = {}
    st.session_state.intake_existing_mother_id = None
    st.rerun()

# =============================================================================
# SECTION: Helper Logic - ID Generation (Clue Chain)
# =============================================================================

def generate_ids():
    """Generates the Clue Chain IDs based on current session state."""
    m = st.session_state.intake_mother
    b = st.session_state.intake_bin
    
    # Mother ID: [Name]_[Species]_[YYYYMMDD]
    m_name_slug = m['name'].replace(" ", "")
    m_date_slug = m['date'].strftime('%Y%m%d')
    mother_id = f"{m_name_slug}_{m['species_id']}_{m_date_slug}"
    
    # If we are using an existing mother, we use that ID instead
    if st.session_state.intake_existing_mother_id:
        mother_id = st.session_state.intake_existing_mother_id
        
    # Bin ID: [MotherID]_[HarvestDateSlug]
    b_date_slug = b['date'].strftime('%Y%m%d')
    bin_id = f"{mother_id}_{b_date_slug}"
    
    # Egg IDs: [BinID]_E[#]
    egg_ids = [f"{bin_id}_E{str(i+1).zfill(2)}" for i in range(b['count'])]
    
    return mother_id, bin_id, egg_ids

# =============================================================================
# SECTION: Wizard Steps
# =============================================================================

def show_step_1():
    st.markdown("<h1>New Intake — Step 1: Mother</h1>", unsafe_allow_html=True)
    supabase = get_supabase_client()
    
    # Fetch Species
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
        
        if st.form_submit_button("NEXT: ASSIGN BIN & INCUBATOR"):
            if not m_name:
                st.error("❌ Name is required.")
            else:
                st.session_state.intake_mother = {
                    'name': m_name, 'species_id': species_map[m_species_name], 'species_name': m_species_name,
                    'condition': m_cond, 'date': m_date, 'location': m_loc, 'notes': m_notes
                }
                try:
                    dup = supabase.table("mother").select("*").ilike("mother_name", m_name).eq("species_id", species_map[m_species_name]).execute()
                    if dup.data: st.session_state['duplicate_found'] = dup.data[0]
                    else: 
                        st.session_state['duplicate_found'] = None
                        next_step(); st.rerun()
                except: next_step(); st.rerun()

    if st.session_state.get('duplicate_found'):
        d = st.session_state['duplicate_found']
        st.warning(f"⚠️ Mother '{d['mother_name']}' already exists.")
        c1, c2 = st.columns(2)
        if c1.button("✅ USE EXISTING"): 
            st.session_state.intake_existing_mother_id = d['mother_id']
            st.session_state.duplicate_found = None
            next_step(); st.rerun()
        if c2.button("✏️ CREATE NEW"): 
            st.session_state.intake_existing_mother_id = None
            st.session_state.duplicate_found = None
            next_step(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def show_step_2():
    st.markdown("<h1>New Intake — Step 2: Bin Setup</h1>", unsafe_allow_html=True)
    supabase = get_supabase_client()
    
    # Incubators
    inc_data = []
    try: res = supabase.table("incubator").select("incubator_id, label").eq("is_active", True).execute(); inc_data = res.data
    except: inc_data = [{"incubator_id": "INC-01", "label": "Incubator Alpha"}]
    inc_map = {i['label']: i['incubator_id'] for i in inc_data}

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    with st.form("bin_form"):
        c1, c2 = st.columns(2)
        b_date = c1.date_input("Harvest Date", value=st.session_state.intake_bin.get('date', datetime.now()))
        b_inc_label = c2.selectbox("Incubator Unit", options=list(inc_map.keys()), 
                                    index=list(inc_map.keys()).index(st.session_state.intake_bin.get('inc_label')) if st.session_state.intake_bin.get('inc_label') in inc_map else 0)
        c3, c4 = st.columns(2)
        b_subs = c3.selectbox("Substrate", ["Vermiculite", "Perlite", "Moss", "Sand Mix"], index=0)
        b_label = c4.text_input("Bin Label", value=st.session_state.intake_bin.get('label', ''))
        b_count = st.number_input("Egg Count", 1, 100, st.session_state.intake_bin.get('count', 10))
        
        bc1, bc2 = st.columns(2)
        if bc1.form_submit_button("◀ BACK"): prev_step(); st.rerun()
        if bc2.form_submit_button("▶ NEXT"): 
            st.session_state.intake_bin = {'date': b_date, 'incubator_id': inc_map[b_inc_label], 'inc_label': b_inc_label, 'substrate': b_subs, 'label': b_label, 'count': b_count}
            next_step(); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def show_step_3_4():
    st.markdown("<h1>New Intake — Review & Confirm</h1>", unsafe_allow_html=True)
    supabase = get_supabase_client()
    
    m_id, b_id, egg_ids = generate_ids()
    
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown(f"### 📋 Summary Preview")
    st.markdown(f"**Mother ID:** `{m_id}` {'(Existing)' if st.session_state.intake_existing_mother_id else '(New)'}")
    st.markdown(f"**Bin ID:** `{b_id}`")
    st.markdown(f"**Egg Records:** {len(egg_ids)} to be generated")
    
    with st.expander("🔍 Preview Egg IDs"):
        st.write(egg_ids)

    c1, c2 = st.columns(2)
    if c1.button("◀ BACK TO BIN"): prev_step(); st.rerun()
    if c2.button("💾 SAVE INTAKE & REGISTER EGGS"):
        def db_transaction():
            # 1. Mother
            if not st.session_state.intake_existing_mother_id:
                m = st.session_state.intake_mother
                supabase.table("mother").insert({
                    "mother_id": m_id, "mother_name": m['name'], "species_id": m['species_id'],
                    "intake_date": m['date'].isoformat(), "condition": m['condition'],
                    "harvest_location": m['location'], "clinical_notes": m['notes']
                }).execute()
            
            # 2. Bin
            b = st.session_state.intake_bin
            supabase.table("bin").insert({
                "bin_id": b_id, "mother_id": m_id, "harvest_date": b['date'].isoformat(),
                "incubator_id": b['incubator_id'], "substrate": b['substrate'], "bin_label": b['label']
            }).execute()
            
            # 3. Eggs
            egg_payloads = [{"egg_id": eid, "bin_id": b_id, "current_stage": "Intake", "status": "Active"} for eid in egg_ids]
            supabase.table("egg").insert(egg_payloads).execute()
            return len(egg_ids)

        try:
            count = logged_write(supabase, st.session_state.session_id, "INTAKE_TRANSACTION", 
                                {"mother_id": m_id, "bin_id": b_id, "egg_count": len(egg_ids)}, db_transaction)
            st.balloons()
            st.success(f"✅ Successfully registered {count} eggs to Bin {b_id}.")
            if st.button("Start New Intake"): reset_wizard()
        except Exception as e: st.error(f"❌ Transaction Failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Router ---
if not st.session_state.get("logged_in"): st.warning("⚠️ Select an observer to continue."); st.stop()
if st.session_state.intake_step == 1: show_step_1()
elif st.session_state.intake_step == 2: show_step_2()
else: show_step_3_4()
