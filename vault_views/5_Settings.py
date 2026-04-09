"""
=============================================================================
Module:     vault_views/5_Settings.py (GOLD EDITION - v7.2.1)
Project:    Incubator Vault v7.2.1 — WINC
Purpose:    Hardened Lookup CRUD with Mid-Season Performance Locking.
Revision:   2026-04-08 — Gold Master Release (Antigravity)
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase = bootstrap_page("Settings", "⚙️")

st.title("⚙️ Vault Administration")

# =============================================================================
# SECTION: 🔒 Mid-Season Lock Proofing (§4.42)
# =============================================================================
active_res = supabase.table('egg').select('id', count='exact').eq('status', 'Active').execute()
is_locked = active_res.count > 0

if is_locked:
    st.error(f"🔒 **MID-SEASON LOCK ACTIVE**: {active_res.count} active subjects detected. Lookup tables are READ-ONLY.")
else:
    st.success("🔓 **MAINTENANCE MODE**: Lookups are editable (Draft Stage).")

# =============================================================================
# REQ 1725: Mobile Accessibility (Persistent)
# =============================================================================
st.sidebar.header("Accessibility")
font_size = st.sidebar.slider("Global Font Scale", 12, 24, 16)
st.markdown(f"<style>body, .stText {{ font-size: {font_size}px; }}</style>", unsafe_allow_html=True)

# =============================================================================
# DATA OPERATIONS: Hardened CRUD Matrix
# =============================================================================
tabs = st.tabs(["🛡️ Species Registry", "🌡️ Development Stages", "📜 Audit Log"])

with tabs[0]:
    st.subheader("Species Management")
    res = supabase.table('species').select("*").execute()
    df = pd.DataFrame(res.data)
    
    # Use st.data_editor with strict disable logic
    edited_df = st.data_editor(
        df,
        disabled=list(df.columns) if is_locked else ["species_id"],
        num_rows="dynamic" if not is_locked else "fixed",
        key="species_editor"
    )
    
    if not is_locked and st.button("💾 Synchronize Species Changes"):
        def sync_species():
            # Get only the modified rows from st.data_editor state
            to_upsert = []
            
            # Using data_editor automatically captures changes. We iterate over the dataframe.
            # In Streamlit, data_editor returns the FULL edited dataframe.
            for idx, row in edited_df.iterrows():
                to_upsert.append({
                    "species_id": row["species_id"],
                    "common_name": row["common_name"],
                    "scientific_name": row["scientific_name"],
                    "species_code": row["species_code"],
                    "vulnerability_status": row["vulnerability_status"]
                })
            
            if to_upsert:
                supabase.table('species').upsert(to_upsert).execute()
                st.success(f"{len(to_upsert)} Species records synchronized with main ledger.")
                st.balloons()
            else:
                st.info("No edits detected.")
        
        safe_db_execute("Species Audit", sync_species)

with tabs[1]:
    res_stages = supabase.table('development_stage').select("*").execute()
    st.data_editor(pd.DataFrame(res_stages.data), disabled=True if is_locked else [])

with tabs[2]:
    st.subheader("System Access Log (Last 50)")
    logs = supabase.table('SystemLog').select("*").order('timestamp', desc=True).limit(50).execute().data
    st.dataframe(pd.DataFrame(logs), use_container_width=True)
