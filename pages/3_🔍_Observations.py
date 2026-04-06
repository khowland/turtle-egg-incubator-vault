"""
=============================================================================
Module:     pages/3_observations.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Rapid observation logging with multi-select egg grid and batch
            observation panel for recording biological indicators.
            Implements Requirements §5 W2 — the daily-use workflow.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Code Review: Fixed N+1 query, bare excepts,
            added enterprise comments)
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
# Description: All Supabase read operations for the observation page.
#              Optimized to avoid N+1 query patterns.
# =============================================================================

# -----------------------------------------------------------------------------
# Function: load_active_data
# Description: Fetches all active bins with their mother/species for filters
# Returns: list[dict] — bin records with nested mother and species data
# -----------------------------------------------------------------------------
def load_active_data(supabase):
    """Fetches all active bins with mother and species data for cascading filters.
    
    Returns:
        list[dict]: Bin records with nested mother→species relationships.
    """
    try:
        res = supabase.table("bin").select(
            "bin_id, bin_label, mother:mother_id(mother_id, mother_name, species:species_id(common_name))"
        ).eq("is_deleted", False).execute()
        return res.data
    except Exception as e:
        # Show error to user — don't silently return empty data
        st.error(f"⚠️ Failed to load bin/mother data: {e}")
        return []

# -----------------------------------------------------------------------------
# Function: load_eggs_with_latest_obs
# Description: Fetches all active eggs and their latest observations in TWO
#              queries instead of N+1. First query gets eggs, second gets the
#              latest observation per egg using a single batch query.
# Params: supabase (Client), bin_id (str, optional)
# Returns: list[dict] — eggs enriched with latest_obs and age_days
# -----------------------------------------------------------------------------
def load_eggs_with_latest_obs(supabase, bin_id=None):
    """Fetches eggs with their latest observation — optimized to 2 queries.
    
    Instead of querying EggObservation once per egg (N+1 problem), this
    fetches all eggs first, then batch-fetches the latest observation for
    all egg_ids in a single query.
    
    Args:
        supabase: Supabase client instance.
        bin_id: Optional bin_id to filter eggs. None = all active eggs.
        
    Returns:
        list[dict]: Egg records enriched with 'latest_obs' and 'age_days'.
    """
    try:
        # Query 1: Fetch all active eggs with bin harvest date
        query = supabase.table("egg").select(
            "egg_id, current_stage, status, bin:bin_id(bin_id, bin_label, harvest_date)"
        ).eq("is_deleted", False).eq("status", "Active")
        
        if bin_id:
            query = query.eq("bin_id", bin_id)
        
        res = query.execute()
        eggs = res.data
        
        if not eggs:
            return []
        
        # Query 2: Batch-fetch ALL latest observations in one query
        # This replaces the N+1 pattern (1 query per egg → 1 query total)
        egg_ids = [e['egg_id'] for e in eggs]
        obs_res = supabase.table("EggObservation").select(
            "egg_id, chalking, vascularity, molding, leaking, dented, discolored, stage_at_observation, notes, timestamp"
        ).in_("egg_id", egg_ids).order("timestamp", desc=True).execute()
        
        # Build a map: egg_id → latest observation (first occurrence per egg_id)
        latest_obs_map = {}
        for obs in obs_res.data:
            if obs['egg_id'] not in latest_obs_map:
                # First hit is the latest due to ORDER BY timestamp DESC
                latest_obs_map[obs['egg_id']] = obs
        
        # Enrich each egg with its latest observation and calculated age
        for egg in eggs:
            egg['latest_obs'] = latest_obs_map.get(egg['egg_id'], {})
            
            # Calculate age in days from harvest date
            try:
                harvest_date = datetime.fromisoformat(egg['bin']['harvest_date'].split('+')[0])
                egg['age_days'] = (datetime.now().date() - harvest_date.date()).days
            except (ValueError, TypeError, KeyError):
                egg['age_days'] = 0  # Fallback if date parsing fails
        
        return eggs
        
    except Exception as e:
        st.error(f"⚠️ Failed to load egg data: {e}")
        return []

# =============================================================================
# SECTION: UI Components — Filter Bar & Egg Grid
# Description: Renders the filter bar (mother/bin cascading dropdowns) and
#              the egg card grid with multi-select checkboxes.
# =============================================================================

st.markdown("<h1>Neural Observation Engine</h1>", unsafe_allow_html=True)

# Requirement §6: Block all writes if no observer selected
if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please select an observer in the sidebar to enable observation logging.")
    st.stop()

supabase = get_supabase_client()
raw_data = load_active_data(supabase)

# --- FILTER BAR ---
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 2, 1])

# Build mother list from bin data (deduplicated, sorted)
mother_list = sorted(list(set([d['mother']['mother_name'] for d in raw_data]))) if raw_data else []
sel_mother = c1.selectbox("🐢 Filter by Mother", ["All"] + mother_list)

# Cascading filter: bins are filtered by selected mother
bin_options = ["All"]
if sel_mother != "All":
    bin_options += sorted(list(set([
        d['bin_label'] or d['bin_id'] 
        for d in raw_data 
        if d['mother']['mother_name'] == sel_mother
    ])))
sel_bin = c2.selectbox("📦 Filter by Bin", bin_options)

if c3.button("🔄 REFRESH DATA"):
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# Resolve selected bin to bin_id for query filtering
filter_bin_id = None
if sel_bin != "All":
    try:
        filter_bin_id = next(d['bin_id'] for d in raw_data if (d['bin_label'] or d['bin_id']) == sel_bin)
    except StopIteration:
        st.warning(f"⚠️ Could not resolve bin '{sel_bin}'. Showing all eggs.")

# Load eggs with optimized 2-query approach
egg_data = load_eggs_with_latest_obs(supabase, bin_id=filter_bin_id)

if not egg_data:
    st.info("📭 No active eggs found for the selected filters.")
else:
    st.markdown(f"### 🥚 Active Eggs ({len(egg_data)})")
    
    # Initialize multi-select state
    if 'selected_eggs' not in st.session_state:
        st.session_state.selected_eggs = set()
    
    # --- EGG CARD GRID ---
    # Layout: 4 columns on desktop, wraps naturally on mobile
    cols = st.columns(4)
    for idx, egg in enumerate(egg_data):
        with cols[idx % 4]:
            # Determine if egg has critical health flags for visual alert
            is_critical = egg['latest_obs'].get('molding') or egg['latest_obs'].get('leaking')
            card_class = "glass-card alert-critical" if is_critical else "glass-card"
            
            st.markdown(f"<div class='{card_class}'>", unsafe_allow_html=True)
            st.markdown(f"**{egg['egg_id']}**")
            st.caption(f"Stage: {egg['current_stage']}")
            
            # Chalking indicator: ●○ visual scale (0-2)
            chalk = egg['latest_obs'].get('chalking', 0) or 0
            chalk_dots = "●" * int(chalk) + "○" * (2 - int(chalk))
            st.markdown(f"Chalk: {chalk_dots} ({chalk})")
            
            # Vascularity indicator: heart = veins visible via candling
            vasc = "❤️ YES" if egg['latest_obs'].get('vascularity') else "⚪ NO"
            st.markdown(f"Vasc: {vasc}")
            st.markdown(f"Age: {egg['age_days']} days")
            
            # Multi-select checkbox per egg
            if st.checkbox("Select", key=f"chk_{egg['egg_id']}"): 
                st.session_state.selected_eggs.add(egg['egg_id'])
            else:
                st.session_state.selected_eggs.discard(egg['egg_id'])
            
            # --- PER-EGG OBSERVATION HISTORY ---
            # Expandable timeline showing all past observations for this egg
            with st.expander("📋 History"):
                try:
                    h_res = supabase.table("EggObservation").select(
                        "*, observer:observer_id(display_name)"
                    ).eq("egg_id", egg['egg_id']).order("timestamp", desc=True).execute()
                    
                    if h_res.data:
                        for h in h_res.data:
                            # Parse timestamp for human-readable display
                            t = datetime.fromisoformat(h['timestamp'].split('+')[0]).strftime("%b %d, %I:%M %p")
                            obs_name = h.get('observer', {}).get('display_name', 'Unknown') if h.get('observer') else 'Unknown'
                            st.caption(f"**{t}** | {obs_name}")
                            
                            # Health indicator summary line
                            chalk_val = h.get('chalking', '?')
                            vasc_val = 'YES' if h.get('vascularity') else 'NO'
                            flags = []
                            if h.get('molding'): flags.append("🍄 Mold")
                            if h.get('leaking'): flags.append("💧 Leak")
                            if h.get('dented'): flags.append("⚠️ Dent")
                            if h.get('discolored'): flags.append("🟡 Disc")
                            flag_str = f" | {', '.join(flags)}" if flags else ""
                            
                            st.markdown(f"Chalk: {chalk_val}, Vasc: {vasc_val}{flag_str}")
                            if h.get('notes'):
                                st.markdown(f"*Notes: {h['notes']}*")
                            st.divider()
                    else:
                        st.caption("No observation history for this egg.")
                except Exception as e:
                    st.caption(f"Error loading history: {e}")
            
            st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# SECTION: Batch Observation Panel
# Description: Appears when ≥1 egg is selected. Allows applying common
#              observation values to all selected eggs in one action.
#              Per Requirements §5 W2: "skip" = no change for that property.
# =============================================================================

if st.session_state.get('selected_eggs'):
    st.markdown("---")
    st.markdown("<div class='glass-card' style='border: 2px solid #10B981;'>", unsafe_allow_html=True)
    st.markdown(f"### 📝 BATCH OBSERVATION ({len(st.session_state.selected_eggs)} selected)")
    
    with st.form("obs_form"):
        # --- Biological Indicator Fields ---
        c1, c2 = st.columns(2)
        f_chalk = c1.selectbox("Chalking", ["— (skip)", "0: None", "1: Partial", "2: Full"])
        f_vasc = c2.selectbox("Vascularity", ["— (skip)", "YES", "NO"])
        
        # --- Health Flag Toggles ---
        # Default OFF — toggle ON to flag a health concern
        st.markdown("**Health Flags** _(toggle ON to flag concerns)_")
        h1, h2, h3, h4 = st.columns(4)
        f_mold = h1.toggle("🍄 Mold")
        f_leak = h2.toggle("💧 Leak")
        f_dent = h3.toggle("⚠️ Dent")
        f_disc = h4.toggle("🟡 Discolor")
        
        # --- Stage & Status Transitions ---
        s1, s2 = st.columns(2)
        f_stage = s1.selectbox(
            "Stage Transition", 
            ["— (keep current)", "Intake", "Developing", "Vascular", "Mature", "Pipping", "Hatched"]
        )
        f_status = s2.selectbox(
            "Status Update", 
            ["— (keep current)", "Active", "Dead", "Hatched"]
        )
        
        # --- Notes ---
        f_notes = st.text_area("Observation Notes")
        
        if st.form_submit_button("💾 SAVE OBSERVATION FOR BATCH"):
            # Build observation payload — "skip" values become None (not recorded)
            obs_payload = {
                "chalking": int(f_chalk[0]) if "skip" not in f_chalk else None,
                "vascularity": True if f_vasc == "YES" else (False if f_vasc == "NO" else None),
                "molding": f_mold,
                "leaking": f_leak,
                "dented": f_dent,
                "discolored": f_disc,
                "notes": f_notes if f_notes else None,
                "observer_id": st.session_state.observer_id
            }
            
            def db_save():
                """Insert one EggObservation row per selected egg.
                
                If stage or status changed, also UPDATE the egg table.
                This is the core batch-write operation for the observation workflow.
                """
                saved_count = 0
                for eid in st.session_state.selected_eggs:
                    # Build per-egg payload with egg-specific fields
                    payload = obs_payload.copy()
                    payload['egg_id'] = eid
                    payload['session_id'] = st.session_state.session_id
                    
                    # Record the egg's stage at time of observation (for longitudinal analysis)
                    current_egg = next((e for e in egg_data if e['egg_id'] == eid), None)
                    payload['stage_at_observation'] = current_egg['current_stage'] if current_egg else 'Unknown'
                    
                    # Insert append-only observation record
                    supabase.table("EggObservation").insert(payload).execute()
                    
                    # Update egg table if stage or status changed
                    egg_update = {}
                    if "keep" not in f_stage:
                        egg_update['current_stage'] = f_stage
                    if "keep" not in f_status:
                        egg_update['status'] = f_status
                    
                    if egg_update:
                        egg_update['updated_by_session'] = st.session_state.session_id
                        supabase.table("egg").update(egg_update).eq("egg_id", eid).execute()
                    
                    saved_count += 1
                return saved_count

            try:
                count = logged_write(
                    supabase, st.session_state.session_id, "OBSERVATION_BATCH", 
                    {"egg_ids": list(st.session_state.selected_eggs), "changes": obs_payload}, 
                    db_save
                )
                st.success(f"✅ Successfully logged {count} observations.")
                st.session_state.selected_eggs.clear()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to save observation batch: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
