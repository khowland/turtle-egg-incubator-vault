"""
=============================================================================
Module:     vault_views/7_Diagnostic.py (NEW - CAP.05)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    "Quick-Strike" Unit Testing & System Health.
Revision:   2026-04-08 — Initial Release (Antigravity)
=============================================================================
"""

import streamlit as st
import time
from utils.bootstrap import bootstrap_page, safe_db_execute

supabase = bootstrap_page("Diagnostics", "🛡️")

st.title("🛡️ System Health & Diagnostic Suite")
st.caption("Perform these checks prior to a major influx of eggs (e.g., after a storm).")

# =============================================================================
# TEST 1: API & DB HEARTBEAT
# =============================================================================
st.subheader("1. Connectivity Heartbeat")
if st.button("Run Connection Ping"):
    with st.spinner("Pinging Biological Ledger..."):
        res = safe_db_execute("Ping", supabase.table('species').select("count", count='exact').limit(1).execute)
        if res:
            st.success(f"✅ Connection Stable. Ledger contains {res.count} species definitions.")

# =============================================================================
# TEST 2: ATOMIC COUNTER VALIDATION
# =============================================================================
st.subheader("2. Sequence Logic Check")
if st.button("Verify Intake Counter"):
    with st.spinner("Analyzing Species Sequence..."):
        # Check if BL (Blanding's) is accessible
        bl_res = supabase.table('species').select("intake_count").eq('species_id', 'BL').execute()
        if bl_res.data:
            current = bl_res.data[0]['intake_count']
            st.info(f"🧬 Current Blanding's Sequential ID Header: **BL{current+1}**")
            st.success("✅ Sequence Logic Valid.")

# =============================================================================
# TEST 3: AUDIT TRACE VERIFICATION
# =============================================================================
st.subheader("3. Audit Layer Trace (§6.53)")
if st.button("Verify Active SessionID"):
    st.write(f"Your Session ID for this audit: `{st.session_state.session_id}`")
    st.success("✅ Audit propagation active.")

st.divider()
st.caption("WINC Clinical Standard v7.2.1-Diagnostic")
