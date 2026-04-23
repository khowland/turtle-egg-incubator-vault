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
from pathlib import Path
import streamlit as st
from utils.session import init_session
from utils.bootstrap import bootstrap_page, VERSION
from utils.rbac import can_elevated_clinical_operations

# v8.0.0 Global Entry: Mount CSS Early to eliminate flickering
bootstrap_page("WINC Incubator", "🐢", render_sidebar=False)
init_session()

# --- WINC Logo: pinned to top-left of sidebar via st.logo() ---
# Uses Path(__file__).parent for absolute path resolution on Streamlit Cloud.
# st.logo() is the ONLY official Streamlit API for placing content above
# st.navigation() links. st.sidebar.image() and st.sidebar.markdown() always
# render BELOW nav links when st.navigation() is active (by design).
_logo_path = Path(__file__).parent / "assets" / "winc-logo2.png"
if _logo_path.exists():
    st.logo(str(_logo_path))

# --- Bottom sidebar: user identity + version + SHIFT END ---
# NOTE: With st.navigation(), ALL st.sidebar.* content appears BELOW nav links
# regardless of call order. This is Streamlit's intended behaviour.
# The user/version block is intentionally at the bottom, tucked below nav,
# with a spacer for visual breathing room (per CR-20260423).
if st.session_state.get("observer_id"):
    # Spacer pushes identity block visually away from nav items
    st.sidebar.markdown(
        "<div style='margin-top: 2rem; padding-top: 0.5rem; border-top: 1px solid #1e293b;'>"
        f"<span style='font-size: 0.9em; font-weight: 600;'>👤 {st.session_state.get('observer_name', 'User')}</span><br>"
        f"<span style='font-size: 0.72em; color: #475569;'>{VERSION}</span>"
        "</div>",
        unsafe_allow_html=True,
    )

# Navigation definition
if not st.session_state.get("observer_id"):
    pages = [st.Page("vault_views/0_Login.py", title="Welcome", icon="🐢")]
else:
    pages = [
        st.Page("vault_views/1_Dashboard.py", title="Today's Summary", icon="📊"),
        st.Page("vault_views/2_New_Intake.py", title="Intake", icon="🐣"),
        st.Page("vault_views/3_Observations.py", title="Observations", icon="🔍"),
        st.Page("vault_views/5_Settings.py", title="Settings", icon="⚙️"),
        st.Page("vault_views/6_Reports.py", title="Reports", icon="📈"),
    ]
    pages.append(st.Page("vault_views/7_Diagnostic.py", title="System Check", icon="🩺"))
    pages.append(st.Page("vault_views/8_Help.py", title="Help", icon="📚"))

pg = st.navigation(pages)
pg.run()
