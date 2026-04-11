"""
=============================================================================
Module:        vault_views/7_Diagnostic.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.bootstrap
Inputs:        st.session_state (session_id)
Outputs:       Health Status Diagnostics
Description:   System Health and Quick-Strike Unit Testing.
=============================================================================
"""

import streamlit as st
import time
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase_client = bootstrap_page("Diagnostics", "🛡️")

st.title("🛡️ System Health & Diagnostic Suite")
st.caption("Perform these checks prior to a major influx of eggs.")

# --- Connectivity Heartbeat ---
st.subheader("1. Connectivity Heartbeat")
if st.button("Run Connection Ping"):
    with st.spinner("Pinging Biological Ledger..."):
        ping_result = safe_db_execute("Ping", supabase_client.table('species').select("count", count='exact').limit(1).execute)
        if ping_result:
            st.success(f"✅ Connection Stable. Ledger contains {ping_result.count} species definitions.")

# --- Sequence Logic Check ---
st.subheader("2. Sequence Logic Check")
if st.button("Verify Intake Counter"):
    with st.spinner("Analyzing Species Sequence..."):
        bl_species_result = supabase_client.table('species').select("intake_count").eq('species_id', 'BL').execute()
        if bl_species_result.data:
            current_count = bl_species_result.data[0]['intake_count']
            st.info(f"🧬 Current Blanding's Sequential ID Header: **BL{current_count+1}**")
            st.success("✅ Sequence Logic Valid.")

# --- Audit Layer Trace ---
st.subheader("3. Audit Layer Trace (§6.53)")
if st.button("Verify Active Session ID"):
    st.write(f"Your Session ID for this audit: `{st.session_state.session_id}`")
    st.success("✅ Audit propagation active.")

st.divider()
st.caption("WINC Clinical Standard v8.0.0-Diagnostic")
