"""
=============================================================================
Module:        vault_views/7_Diagnostic.py
Project:       Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (session_id)
Outputs:       Health Status Diagnostics
Description:   System health checks prior to peak intake; navigation gated in app.py.
=============================================================================
"""

import streamlit as st
from utils.bootstrap import bootstrap_page, safe_db_execute
from utils.performance import track_view_performance

supabase_client = bootstrap_page("Diagnostics", "🛡️")

with track_view_performance("Diagnostic"):
    st.title("🛡️ System Health & Diagnostic Suite")
    st.caption("Perform these checks prior to a major influx of eggs.")

    # --- Connectivity Heartbeat ---
    st.subheader("1. Connectivity Heartbeat")
    if st.button("START", help="Run Connection Ping", type="primary"):
        with st.spinner("Pinging Biological Ledger..."):

            def run_ping():
                return (
                    supabase_client.table("species")
                    .select("species_id", count="exact")
                    .limit(1)
                    .execute()
                )

            ping_result = safe_db_execute("Ping", run_ping)
            if ping_result is not None:
                st.success(
                    f"✅ Connection stable. Species registry rows: **{ping_result.count or 0}**."
                )

    # --- Sequence Logic Check ---
    st.subheader("2. Sequence Logic Check")
    if st.button("START", help="Verify Intake Counter", type="primary"):
        with st.spinner("Analyzing species sequence..."):
            bl_species_result = (
                supabase_client.table("species")
                .select("intake_count")
                .eq("species_id", "BL")
                .execute()
            )
            if bl_species_result.data:
                current_count = bl_species_result.data[0]["intake_count"]
                st.info(
                    f"🧬 Current Blanding's sequential header: **BL{current_count + 1}**"
                )
                st.success("✅ Sequence logic valid.")

    # --- Audit Layer Trace (§6.53)
    st.subheader("3. Audit Layer Trace (§6.53)")
    if st.button("START", help="Verify System Logs", type="primary"):
        st.write(f"Active Session ID: `{st.session_state.session_id}`")
        
        def fetch_logs():
            return (
                supabase_client.table("system_log")
                .select("*")
                .order("timestamp", desc=True)
                .limit(10)
                .execute()
            )
        
        logs_result = safe_db_execute("Fetch Logs", fetch_logs)
        if logs_result and logs_result.data:
            st.table(logs_result.data)
            st.success("✅ Audit propagation active.")
        else:
            st.warning("⚠️ No recent logs found in this context.")

    st.divider()
    st.caption("WINC Clinical Standard v8.1.0 — Diagnostic")
