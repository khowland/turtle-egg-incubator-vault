"""
=============================================================================
Module:        app.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.session
Inputs:        st.session_state (observer_id)
Outputs:       st.navigation
Description:   Core router mapping the session states to Views.
=============================================================================
"""
import streamlit as st
from utils.session import init_session
from utils.bootstrap import bootstrap_page

# v8.0.0 Global Entry: Mount CSS Early to eliminate flickering
bootstrap_page("Incubator Vault | WINC", "🐢")
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
        st.Page("vault_views/6_Reports.py", title="Reports", icon="📈"),
        st.Page("vault_views/8_Help.py", title="Help & Manual", icon="📚")
    ]

pg = st.navigation(pages)
pg.run()
