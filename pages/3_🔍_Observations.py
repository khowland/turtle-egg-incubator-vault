"""
=============================================================================
Module:     pages/3_observations.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Daily egg observation logging. This is the most-used page —
            staff stands at the incubator with a phone and logs what they
            see. Designed for portrait phone, single-column, minimal taps.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Mobile-first rewrite for field staff usability)
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
st.set_page_config(page_title="Observations | Incubator Vault", page_icon="🔍", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_sidebar()

# =============================================================================
# SECTION: Database Queries
# Description: Optimized 2-query approach — one for eggs, one batch for all
#              latest observations. No N+1 queries.
# =============================================================================

def load_bins(supabase):
    """Fetch all active bins with mother info for the filter dropdown."""
    try:
        res = supabase.table("bin").select(
            "bin_id, bin_label, mother:mother_id(mother_id, mother_name)"
        ).eq("is_deleted", False).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.error(f"Failed to load bins: {e}")
        return []

def load_eggs(supabase, bin_id=None):
    """Fetch active eggs with latest observation data (2 queries total)."""
    try:
        query = supabase.table("egg").select(
            "egg_id, current_stage, status, bin:bin_id(bin_id, bin_label, harvest_date)"
        ).eq("is_deleted", False).eq("status", "Active")
        
        if bin_id:
            query = query.eq("bin_id", bin_id)
        
        res = query.execute()
        eggs = res.data if res.data else []
        
        if not eggs:
            return []
        
        # Batch-fetch latest observations (1 query for ALL eggs)
        egg_ids = [e['egg_id'] for e in eggs]
        obs_res = supabase.table("EggObservation").select(
            "egg_id, chalking, vascularity, molding, leaking, dented, discolored, notes, timestamp"
        ).in_("egg_id", egg_ids).order("timestamp", desc=True).execute()
        
        # Map: egg_id → most recent observation
        latest = {}
        for obs in (obs_res.data or []):
            if obs['egg_id'] not in latest:
                latest[obs['egg_id']] = obs
        
        # Enrich each egg
        for egg in eggs:
            egg['obs'] = latest.get(egg['egg_id'], {})
            try:
                hd = datetime.fromisoformat(egg['bin']['harvest_date'].split('+')[0])
                egg['age'] = (datetime.now().date() - hd.date()).days
            except:
                egg['age'] = 0
        
        return eggs
    except Exception as e:
        logger.error(f"Failed to load eggs: {e}")
        return []

# =============================================================================
# SECTION: Page UI
# Description: Single-column portrait layout for phone use at the incubator.
#              Flow: Filter → Select eggs → Log observation → Save
# =============================================================================

st.markdown("## 🔍 Egg Observations")

# Block access if no one is logged in
if not st.session_state.get("logged_in"):
    st.warning("⬆️ Pick your name in the sidebar first.")
    st.stop()

supabase = get_supabase_client()

# --- STEP 1: PICK A BIN ---
# Single dropdown — most staff work one bin at a time
bins = load_bins(supabase)
bin_options = {(b['bin_label'] or b['bin_id']): b['bin_id'] for b in bins}
mother_labels = {(b['bin_label'] or b['bin_id']): b.get('mother', {}).get('mother_name', '') for b in bins}

# Show mother name alongside bin label for context
display_options = [f"{label}  ({mother_labels[label]})" for label in bin_options.keys()]

selected_display = st.selectbox(
    "📦 Which bin are you observing?",
    options=["-- Pick a bin --"] + display_options
)

if selected_display == "-- Pick a bin --":
    st.info("👆 Select a bin to see its eggs.")
    st.stop()

# Resolve selected bin to bin_id
selected_label = list(bin_options.keys())[display_options.index(selected_display)]
selected_bin_id = bin_options[selected_label]

# --- STEP 2: SEE THE EGGS ---
egg_data = load_eggs(supabase, bin_id=selected_bin_id)

if not egg_data:
    st.info("📭 No active eggs in this bin.")
    st.stop()

st.markdown(f"**{len(egg_data)} eggs** in {selected_label}")

# Initialize selection state
if 'selected_eggs' not in st.session_state:
    st.session_state.selected_eggs = set()

# --- EGG LIST: Simple scrollable checklist (not a card grid) ---
# Each egg is one row: checkbox + ID + key stats

# "Select All" toggle at the top for batch convenience
select_all = st.checkbox(f"✅ Select all {len(egg_data)} eggs", key="select_all_toggle")

for egg in egg_data:
    obs = egg['obs']
    eid = egg['egg_id']
    
    # Build a compact status line
    stage = egg['current_stage']
    chalk = obs.get('chalking', '-')
    vasc = "❤️" if obs.get('vascularity') else "⚪"
    age = egg['age']
    
    # Health alert indicators
    alerts = []
    if obs.get('molding'): alerts.append("🍄")
    if obs.get('leaking'): alerts.append("💧")
    alert_str = " ".join(alerts)
    
    # Determine if this should be pre-checked
    is_selected = select_all or (eid in st.session_state.selected_eggs)
    
    # Compact row: checkbox with inline egg summary
    label = f"**{eid}** — {stage} · Chalk:{chalk} · {vasc} · {age}d {alert_str}"
    
    # Use container with critical styling if health flagged
    if alerts:
        st.markdown(f"<div class='glass-card alert-critical' style='padding:10px; margin-bottom:8px;'>", unsafe_allow_html=True)
    
    checked = st.checkbox(label, value=is_selected, key=f"chk_{eid}")
    
    if checked:
        st.session_state.selected_eggs.add(eid)
    else:
        st.session_state.selected_eggs.discard(eid)
    
    if alerts:
        st.markdown("</div>", unsafe_allow_html=True)

# --- STEP 3: LOG WHAT YOU SEE ---
selected_count = len(st.session_state.selected_eggs)

if selected_count == 0:
    st.info("👆 Check the eggs you want to observe, then the form will appear below.")
    st.stop()

st.markdown("---")
st.markdown(f"### 📝 Log observation for {selected_count} egg{'s' if selected_count > 1 else ''}")

with st.form("obs_form"):
    # Chalking and vascularity — the two most common fields
    f_chalk = st.selectbox(
        "Chalking", 
        ["— (no change)", "0: None", "1: Partial", "2: Full"]
    )
    f_vasc = st.selectbox(
        "Vascularity (veins visible?)", 
        ["— (no change)", "YES", "NO"]
    )
    
    # Health flags — only toggle ON if there's a problem
    st.markdown("**Any problems?** _(leave off if egg looks normal)_")
    f_mold = st.toggle("🍄 Mold")
    f_leak = st.toggle("💧 Leaking")
    f_dent = st.toggle("⚠️ Dented")
    f_disc = st.toggle("🟡 Discolored")
    
    # Stage and status — usually don't change day-to-day
    with st.expander("📋 Change stage or status (if needed)"):
        f_stage = st.selectbox(
            "Stage", 
            ["— (keep current)", "Intake", "Developing", "Vascular", "Mature", "Pipping", "Hatched"]
        )
        f_status = st.selectbox(
            "Status", 
            ["— (keep current)", "Active", "Dead", "Hatched"]
        )
    
    # Notes — quick field for anything unusual
    f_notes = st.text_area("Notes (optional)", placeholder="e.g., egg #3 has small crack on top")
    
    # Big save button
    if st.form_submit_button("💾 SAVE"):
        # Build observation payload
        obs_payload = {
            "chalking": int(f_chalk[0]) if "no change" not in f_chalk else None,
            "vascularity": True if f_vasc == "YES" else (False if f_vasc == "NO" else None),
            "molding": f_mold,
            "leaking": f_leak,
            "dented": f_dent,
            "discolored": f_disc,
            "notes": f_notes if f_notes else None,
            "observer_id": st.session_state.observer_id
        }
        
        def db_save():
            """Insert one observation per selected egg, update egg if stage/status changed."""
            count = 0
            for eid in st.session_state.selected_eggs:
                payload = obs_payload.copy()
                payload['egg_id'] = eid
                payload['session_id'] = st.session_state.session_id
                
                # Record what stage the egg WAS at when observed
                current_egg = next((e for e in egg_data if e['egg_id'] == eid), None)
                payload['stage_at_observation'] = current_egg['current_stage'] if current_egg else 'Unknown'
                
                supabase.table("EggObservation").insert(payload).execute()
                
                # Update egg record if stage or status changed
                updates = {}
                if "keep" not in f_stage:
                    updates['current_stage'] = f_stage
                if "keep" not in f_status:
                    updates['status'] = f_status
                if updates:
                    updates['updated_by_session'] = st.session_state.session_id
                    supabase.table("egg").update(updates).eq("egg_id", eid).execute()
                
                count += 1
            return count

        try:
            count = logged_write(
                supabase, st.session_state.session_id, "OBSERVATION_BATCH",
                {"egg_ids": list(st.session_state.selected_eggs), "changes": obs_payload},
                db_save
            )
            st.success(f"✅ Saved {count} observation{'s' if count > 1 else ''}!")
            st.session_state.selected_eggs.clear()
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")
