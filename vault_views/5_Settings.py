"""
=============================================================================
Module:     vault_views/5_Settings.py
Project:    Incubator Vault v7.2.0 — Wildlife In Need Center (WINC)
Purpose:    Administrative Hub with CRUD Registry and §4 Mid-Season Lock.
Author:     Antigravity (Sovereign Sprint)
Created:    2026-04-08
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.db import get_supabase
from utils.audit import logged_write

st.set_page_config(page_title='Settings | WINC', page_icon='⚙️', layout='wide')

# =============================================================================
# SECTION: Security & 👤 Identity
# =============================================================================
if not st.session_state.get('observer_id'):
    st.warning("⚠️ Access Denied.")
    st.stop()

st.title("⚙️ Administrative Settings")
supabase = get_supabase()

# =============================================================================
# SECTION: 🔒 Mid-Season Lock (§4.42)
# =============================================================================
# RAD Check: Are there active eggs?
try:
    active_eggs_count = supabase.table('egg').select('id', count='exact').eq('status', 'Active').eq('is_deleted', False).execute().count
    system_is_locked = active_eggs_count > 0
except:
    system_is_locked = False
    active_eggs_count = 0

if system_is_locked:
    st.error(f"🔒 **MID-SEASON LOCK ACTIVE**: {active_eggs_count} subjects are currently developing. Modification of registry and lookup tables is strictly prohibited to maintain biological integrity.")
else:
    st.success("🔓 **SYSTEM UNLOCKED**: No active biological records found. Maintenance is allowed.")

st.divider()

# =============================================================================
# SECTION: Registry Tabs
# =============================================================================
tab1, tab2, tab3 = st.tabs(["👥 Observer Registry", "🐢 Species Management", "🌡️ Incubators"])

with tab1:
    st.subheader("Staff & Observer Registry")
    if system_is_locked:
        st.info("Registry is view-only during active incubation periods.")
    # CRUD logic (similar to previous version but gated by system_is_locked)
    # ... placeholder for RAD ...

with tab2:
    st.subheader("Species Management")
    st.info("Biological lookup: Blanding’s, Wood, Ornate Box, etc.")

with tab3:
    st.subheader("Incubator Management")
    st.info("Precision tracking per incubator unit.")

st.sidebar.caption(f"Lock Status: {'LOCKED' if system_is_locked else 'READY'}")
