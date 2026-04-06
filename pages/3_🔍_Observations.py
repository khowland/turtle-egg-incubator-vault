"""
=============================================================================
Module:     pages/3_observations.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Rapid observation logging with multi-select egg grid and batch
            observation panel for recording biological indicators.
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
st.set_page_config(page_title="Observations | Vault Pro", page_icon="🔍", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: Database Queries
# =============================================================================

def load_active_data(supabase):
    """Fetches all active mothers and bins for cascading filters."""
    try:
        res = supabase.table("bin").select("bin_id, bin_label, mother:mother_id(mother_id, mother_name, species:species_id(common_name))").eq("is_deleted", False).execute()
        return res.data
    except:
        return []

def load_eggs(supabase, bin_id=None):
    """Fetches eggs with their latest biological observations."""
    query = supabase.table("egg").select(
        "egg_id, current_stage, status, bin:bin_id(bin_id, bin_label, harvest_date)"
    ).eq("is_deleted", False).eq("status", "Active")
    
    if bin_id: query = query.eq("bin_id", bin_id)
    
    res = query.execute()
    eggs = res.data
    
    for egg in eggs:
        obs = supabase.table("EggObservation").select("*").eq("egg_id", egg['egg_id']).order("timestamp", desc=True).limit(1).execute()
        egg['latest_obs'] = obs.data[0] if obs.data else {}
        
        harvest_date = datetime.fromisoformat(egg['bin']['harvest_date'].split('+')[0])
        egg['age_days'] = (datetime.now().date() - harvest_date.date()).days
        
    return eggs

# =============================================================================
# SECTION: UI Components
# =============================================================================

st.markdown("<h1>Neural Observation Engine</h1>", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please select an observer in the sidebar to enable observation logging.")
    st.stop()

supabase = get_supabase_client()
raw_data = load_active_data(supabase)

st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 2, 1])

mother_list = sorted(list(set([d['mother']['mother_name'] for d in raw_data])))
sel_mother = c1.selectbox("🐢 Filter by Mother", ["All"] + mother_list)

bin_options = ["All"]
if sel_mother != "All":
    bin_options = sorted(list(set([d['bin_label'] or d['bin_id'] for d in raw_data if d['mother']['mother_name'] == sel_mother])))
sel_bin = c2.selectbox("📦 Filter by Bin", ["All"] + bin_options)

if c3.button("🔄 REFRESH DATA"): st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

filter_bin_id = None
if sel_bin != "All":
    filter_bin_id = next(d['bin_id'] for d in raw_data if (d['bin_label'] or d['bin_id']) == sel_bin)

egg_data = load_eggs(supabase, bin_id=filter_bin_id)

if not egg_data:
    st.info("📭 No active eggs found for the selected filters.")
else:
    st.markdown(f"### 🥚 Active Eggs ({len(egg_data)})")
    
    if 'selected_eggs' not in st.session_state: st.session_state.selected_eggs = set()
    
    cols = st.columns(4)
    for idx, egg in enumerate(egg_data):
        with cols[idx % 4]:
            is_critical = egg['latest_obs'].get('molding') or egg['latest_obs'].get('leaking')
            card_class = "glass-card alert-critical" if is_critical else "glass-card"
            
            st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
            st.markdown(f"**{egg['egg_id']}**")
            st.caption(f"Stage: {egg['current_stage']}")
            
            chalk = egg['latest_obs'].get('chalking', 0)
            chalk_dots = "●" * int(chalk) + "○" * (2 - int(chalk))
            st.markdown(f"Chalk: {chalk_dots} ({chalk})")
            
            vasc = "❤️ YES" if egg['latest_obs'].get('vascularity') else "⚪ NO"
            st.markdown(f"Vasc: {vasc}")
            st.markdown(f"Age: {egg['age_days']} days")
            
            if st.checkbox("Select", key=f"chk_{egg['egg_id']}"): 
                st.session_state.selected_eggs.add(egg['egg_id'])
            else:
                st.session_state.selected_eggs.discard(egg['egg_id'])
            
            # --- STEP A.5: OBSERVATION HISTORY ---
            with st.expander("📋 History"):
                try:
                    h_res = supabase.table("EggObservation").select("*, observer:observer_id(display_name)").eq("egg_id", egg['egg_id']).order("timestamp", desc=True).execute()
                    if h_res.data:
                        for h in h_res.data:
                            t = datetime.fromisoformat(h['timestamp'].split('+')[0]).strftime("%b %d, %I:%M %p")
                            obs_name = h.get('observer', {}).get('display_name', 'Unknown')
                            st.caption(f"**{t}** | {obs_name}")
                            st.markdown(f"Chalk: {h['chalking']}, Vasc: {'YES' if h['vascularity'] else 'NO'}")
                            if h['notes']: st.markdown(f"*Notes: {h['notes']}*")
                            st.divider()
                    else:
                        st.caption("No history for this egg.")
                except:
                    st.caption("Error loading history.")
            
            st.markdown("</div>", unsafe_allow_html=True)

# --- BATCH OBSERVATION PANEL ---
if st.session_state.selected_eggs:
    st.markdown("--- batch panel ---")
    st.markdown("<div class='glass-card' style='border: 2px solid #10B981;'>", unsafe_allow_html=True)
    st.markdown(f"### 📝 BATCH OBSERVATION ({len(st.session_state.selected_eggs)} selected)")
    
    with st.form("obs_form"):
        c1, c2 = st.columns(2)
        f_chalk = c1.selectbox("Chalking", ["— (skip)", "0: None", "1: Partial", "2: Full"])
        f_vasc = c2.selectbox("Vascularity", ["— (skip)", "YES", "NO"])
        
        st.markdown("**Health Flags**")
        h1, h2, h3, h4 = st.columns(4)
        f_mold = h1.toggle("🍄 Mold")
        f_leak = h2.toggle("💧 Leak")
        f_dent = h3.toggle("⚠️ Dent")
        f_disc = h4.toggle("🟡 Discolor")
        
        s1, s2 = st.columns(2)
        f_stage = s1.selectbox("Stage Transition", ["— (keep current)", "Intake", "Developing", "Vascular", "Mature", "Pipping", "Hatched"])
        f_status = s2.selectbox("Status Update", ["— (keep current)", "Active", "Dead", "Hatched"])
        
        f_notes = st.text_area("Observation Notes")
        
        if st.form_submit_button("💾 SAVE OBSERVATION FOR BATCH"):
            obs_payload = {
                "chalking": int(f_chalk[0]) if "skip" not in f_chalk else None,
                "vascularity": True if f_vasc == "YES" else (False if f_vasc == "NO" else None),
                "molding": f_mold,
                "leaking": f_leak,
                "dented": f_dent,
                "discolored": f_disc,
                "notes": f_notes,
                "observer_id": st.session_state.observer_id
            }
            
            def db_save():
                for eid in st.session_state.selected_eggs:
                    payload = obs_payload.copy()
                    payload['egg_id'] = eid
                    payload['session_id'] = st.session_state.session_id
                    payload['stage_at_observation'] = next(e['current_stage'] for e in egg_data if e['egg_id'] == eid)
                    supabase.table("EggObservation").insert(payload).execute()
                    
                    egg_update = {}
                    if "keep" not in f_stage: egg_update['current_stage'] = f_stage
                    if "keep" not in f_status: egg_update['status'] = f_status
                    
                    if egg_update:
                        egg_update['updated_by_session'] = st.session_state.session_id
                        supabase.table("egg").update(egg_update).eq("egg_id", eid).execute()
                return len(st.session_state.selected_eggs)

            try:
                count = logged_write(supabase, st.session_state.session_id, "OBSERVATION_BATCH", 
                                    {"egg_ids": list(st.session_state.selected_eggs), "changes": obs_payload}, db_save)
                st.success(f"✅ Successfully logged {count} observations.")
                st.session_state.selected_eggs.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to save: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
