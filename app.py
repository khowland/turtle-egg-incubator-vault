"""
=============================================================================
Module:        app.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35, §36]
Upstream:      devtools/a0_models.py
Downstream:    utils.session
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, observer_role)
Outputs:       st.navigation
Description:   Core router mapping the session states to Views; Diagnostics for
               trusted roles only (ISS-10).
=============================================================================
"""

import streamlit as st
from utils.session import init_session
from utils.bootstrap import bootstrap_page
from utils.rbac import can_elevated_clinical_operations

# v8.0.0 Global Entry: Mount CSS Early to eliminate flickering
bootstrap_page("WINC Incubator", "🐢")
init_session()

# Navigation definition
if not st.session_state.get("observer_id"):
    # ONLY Login page visible when not logged in
    pages = [st.Page("vault_views/0_Login.py", title="Welcome", icon="🐢")]
else:
    # Full menu visible when logged in
    pages = [
        st.Page("vault_views/1_Dashboard.py", title="Today's Summary", icon="📊"),
        st.Page("vault_views/2_New_Intake.py", title="New Intake", icon="🐣"),
        st.Page("vault_views/3_Observations.py", title="Daily Checks", icon="🔍"),
        st.Page("vault_views/5_Settings.py", title="Vault Administration", icon="⚙️"),
        st.Page("vault_views/6_Reports.py", title="Egg Reports & Analytics", icon="📈"),
    ]
    pages.append(
        st.Page("vault_views/7_Diagnostic.py", title="System Check", icon="🩺")
    )
    pages.append(st.Page("vault_views/8_Help.py", title="Manual & Help", icon="📚"))

pg = st.navigation(pages)
pg.run()
