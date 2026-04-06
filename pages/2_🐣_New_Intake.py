"""
=============================================================================
Module:     pages/2_new_intake.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    4-Step Intake Wizard for registering mothers, bins, and eggs.
            Implements identity check and living-mother support.
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
if 'intake_existing_mother_id' not in st.session_state: st.session_state.intake_existing_mother_id = None

def next_step(): st.session_state.intake_step += 1
def prev_step(): st.session_state.intake_step -= 1
def reset_wizard():
    st.session_state.intake_step = 1
    st.session_state.intake_mother = {}
    st.session_state.intake_existing_mother_id = None
    if 'intake_bin' in st.session_state: st.session_state.intake_bin = {}

# =============================================================================
# SECTION: Step 1 - Mother Registration
# =============================================================================

def show_step_1():
    st.markdown("<h1>New Intake — Step 1: Mother</h1>", unsafe_allow_html=True)
    
    supabase = get_supabase_client()
    
    # Fetch Species for Dropdown
    species_data = []
    try:
        res = supabase.table("species").select("species_id, common_name").execute()
        species_data = res.data
    except:
        species_data = [{"species_id": "Blandings", "common_name": "Blanding's Turtle"}]

    species_map = {s['common_name']: s['species_id'] for s in species_data}

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    with st.form("mother_form"):
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Mother Name (Origin ID)", 
                               value=st.session_state.intake_mother.get('name', ''),
                               placeholder="e.g. Shelly")
        
        m_species_name = c2.selectbox("Species Class", 
                                      options=list(species_map.keys()),
                                      index=list(species_map.keys()).index(st.session_state.intake_mother.get('species_name')) if st.session_state.intake_mother.get('species_name') in species_map else 0)
        
        c3, c4 = st.columns(2)
        m_cond = c3.selectbox("Condition", 
                              options=["Healthy", "Injured", "DOA", "Post-Mortem Harvest"],
                              index=["Healthy", "Injured", "DOA", "Post-Mortem Harvest"].index(st.session_state.intake_mother.get('condition')) if st.session_state.intake_mother.get('condition') in ["Healthy", "Injured", "DOA", "Post-Mortem Harvest"] else 0)
        
        m_date = c4.date_input("Intake Date", value=st.session_state.intake_mother.get('date', datetime.now()))
        
        m_loc = st.text_input("Harvest Location (GPS or Description)", 
                              value=st.session_state.intake_mother.get('location', ''),
                              placeholder="e.g. Hwy 12 & Cty P")
        
        m_notes = st.text_area("Clinical Notes", 
                               value=st.session_state.intake_mother.get('notes', ''),
                               placeholder="Injury details, cause of death...")
        
        submitted = st.form_submit_button("NEXT: ASSIGN BIN & INCUBATOR")

    if submitted:
        if not m_name or len(m_name) < 2:
            st.error("❌ Please enter a valid Mother Name (min 2 chars).")
        else:
            # Store data in state
            st.session_state.intake_mother = {
                'name': m_name,
                'species_id': species_map[m_species_name],
                'species_name': m_species_name,
                'condition': m_cond,
                'date': m_date,
                'location': m_loc,
                'notes': m_notes
            }
            
            # --- IDENTITY CHECK LOGIC §5 W1 ---
            try:
                dup_res = supabase.table("mother").select("*")\
                    .ilike("mother_name", m_name)\
                    .eq("species_id", species_map[m_species_name])\
                    .eq("is_deleted", False).execute()
                
                if dup_res.data:
                    existing = dup_res.data[0]
                    st.session_state['duplicate_found'] = existing
                else:
                    st.session_state['duplicate_found'] = None
                    next_step()
                    st.rerun()
            except:
                next_step()
                st.rerun()

    # Display Warning if Identity Match Found
    if st.session_state.get('duplicate_found'):
        existing = st.session_state['duplicate_found']
        st.markdown(f"""
        <div style='border: 2px solid #F59E0B; padding: 20px; border-radius: 15px; background: rgba(245, 158, 11, 0.1);'>
            <h3 style='color: #F59E0B; margin-top: 0;'>⚠️ Identity Match Found</h3>
            <p>A mother named <b>{existing['mother_name']}</b> already exists in the registry.</p>
            <p><b>Intake Date:</b> {existing['intake_date']} | <b>Condition:</b> {existing['condition']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        if col_a.button("✅ USE EXISTING — ADD NEW BIN"):
            st.session_state.intake_existing_mother_id = existing['mother_id']
            st.session_state.duplicate_found = None
            next_step()
            st.rerun()
        if col_b.button("✏️ CREATE NEW MOTHER"):
            st.session_state.intake_existing_mother_id = None
            st.session_state.duplicate_found = None
            next_step()
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: Wizard Router
# =============================================================================

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please select an observer in the sidebar to enable intake registration.")
    st.stop()

if st.session_state.intake_step == 1: show_step_1()
else: st.info(f"🚧 Step {st.session_state.intake_step} Coming in next build...")

if st.session_state.intake_step > 1:
    if st.button("🔙 Back to Step 1"):
        st.session_state.intake_step = 1
        st.rerun()
