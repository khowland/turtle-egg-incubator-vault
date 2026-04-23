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

import os
import streamlit as st
from utils.session import init_session
from utils.bootstrap import bootstrap_page, VERSION
from utils.rbac import can_elevated_clinical_operations

# v8.0.0 Global Entry: Mount CSS Early to eliminate flickering
# render_sidebar=False: sidebar identity rendered here in app.py instead,
# so it appears ABOVE st.navigation() links (not below them)
bootstrap_page("WINC Incubator", "🐢", render_sidebar=False)
init_session()

# --- WINC Logo: pinned to absolute top-left of sidebar via st.logo() ---
# st.logo() is the official Streamlit API for top-of-nav logo placement.
# It renders ABOVE all navigation items, unlike st.sidebar.image() which
# gets pushed below nav links when st.navigation() is active.
# CR-20260423: Fixes logo/user not appearing at top of sidebar.
_logo_path = os.path.join(os.path.dirname(__file__), "assets", "winc-logo2.png")
if os.path.exists(_logo_path):
    st.logo(_logo_path)

# --- User identity + version: added to sidebar BEFORE st.navigation() ---
# Content added to st.sidebar before st.navigation() appears between the
# logo and the navigation links — exactly where we want it.
if st.session_state.get("observer_id"):
    st.sidebar.markdown(
        f"<div style='padding: 0.15rem 0 0.5rem 0;'>"
        f"<span style='font-size: 0.95em; font-weight: 600;'>👤 {st.session_state.get('observer_name', 'User')}</span><br>"
        f"<span style='font-size: 0.75em; color: #64748b;'>{VERSION}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.divider()

# Navigation definition
if not st.session_state.get("observer_id"):
    # ONLY Login page visible when not logged in
    pages = [st.Page("vault_views/0_Login.py", title="Welcome", icon="🐢")]
else:
    # Full menu visible when logged in
    pages = [
        st.Page("vault_views/1_Dashboard.py", title="Today's Summary", icon="📊"),
        st.Page("vault_views/2_New_Intake.py", title="Intake", icon="🐣"),
        st.Page("vault_views/3_Observations.py", title="Observations", icon="🔍"),
        st.Page("vault_views/5_Settings.py", title="Settings", icon="⚙️"),
        st.Page("vault_views/6_Reports.py", title="Reports", icon="📈"),
    ]
    pages.append(
        st.Page("vault_views/7_Diagnostic.py", title="System Check", icon="🩺")
    )
    pages.append(st.Page("vault_views/8_Help.py", title="Help", icon="📚"))

pg = st.navigation(pages)
pg.run()
