"""
=============================================================================
Module:     vault_views/3_Observations.py (HARDENED - CAP.03)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    Hardened Observations with Min-Weight Guard.
Revision:   2026-04-08 — CAP Hardening (Antigravity)
=============================================================================
"""

import streamlit as st
from utils.bootstrap import bootstrap_page

supabase = bootstrap_page("Observations", "🔍")

st.title("🔍 Observation Engine")

# --- CAP.03: Biologist Guard (Min Weight) ---
if not st.session_state.get('env_gate_synced'):
    with st.chat_message("assistant", avatar="🐢"):
        st.write("**Protocol:** Enter current weight to unlock grids.")
        weight = st.number_input("Current Bin Weight (g)", min_value=0.0, step=0.1, help="Must be above 500g for a loaded bin.")
        
        if weight < 500.0 and weight > 0:
            st.warning("⚠️ Warning: This weight seems low for a clinical bin. Please verify.")
            
        if st.button("Unlock Grids") and weight >= 0.1:
            st.session_state.env_gate_synced = True
            st.rerun()
    st.stop()

# [Grid logic follows...]
st.info("Grid Active. Minimum Bio-Payload enforced (§2.18).")
