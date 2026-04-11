"""
# ==============================================================================
# Module:        app.py (v7.9.4)
# Project:       Incubator Vault v7.9.4
# Client:        Wildlife In Need Center (WINC)
# Author:        Antigravity (Sovereign Sprint)
# Description:   Core router mapping the session states to Views.
#
# Revision History:
# ------------------------------------------------------------------------------
# Date          Author          Version     Description
# ------------------------------------------------------------------------------
# 2026-04-10    Antigravity     7.9.4       Clinical Sovereignty Edition
# ==============================================================================
"""
import streamlit as st
from utils.session import init_session

st.set_page_config(page_title="Incubator Vault | WINC", page_icon="🐢", layout="wide")

init_session()

# Navigation definition
if not st.session_state.get('observer_id'):
    # ONLY Login page visible when not logged in
    pages = [st.Page("vault_views/0_Login.py", title="Vault Login", icon="🐢")]
else:
    # Full menu visible when logged in
    pages = [
        st.Page("vault_views/1_Dashboard.py", title="Dashboard", icon="📊"),
        st.Page("vault_views/2_New_Intake.py", title="New Intake", icon="🐣"),
        st.Page("vault_views/3_Observations.py", title="Observations", icon="🔍"),
        st.Page("vault_views/5_Settings.py", title="Settings", icon="⚙️"),
        st.Page("vault_views/6_Reports.py", title="Reports", icon="📈")
    ]

pg = st.navigation(pages)
pg.run()
