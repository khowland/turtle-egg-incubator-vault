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
import time
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="WINC Incubator",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SURGICAL DIAGNOSTIC: Start timing before any imports
print(f"[{time.strftime('%H:%M:%S')}] 🔥 app.py: Starting absolute top-level execution")

from utils.session import init_session
from utils.bootstrap import bootstrap_page, get_app_version
# VERSION = get_app_version() # No longer used as a top-level constant to avoid stale cache
from utils.rbac import can_elevated_clinical_operations

print(f"[{time.strftime('%H:%M:%S')}] 🚀 app.py: Core modules imported")

# v8.0.0 Global Entry: Mount CSS Early to eliminate flickering
print(f"[{time.strftime('%H:%M:%S')}] 🛠️ app.py: Calling bootstrap_page")
bootstrap_page("WINC Incubator", "🐢", render_sidebar=False)
print(f"[{time.strftime('%H:%M:%S')}] ✅ app.py: bootstrap_page complete")

print(f"[{time.strftime('%H:%M:%S')}] 🛠️ app.py: Calling init_session")
init_session()
print(f"[{time.strftime('%H:%M:%S')}] ✅ app.py: init_session complete")

# v8.1.4: Minimalist Clinical Standard (No Logo)

# --- Sidebar Footer: User Identity + Version + Logout ---
if st.session_state.get("observer_id"):
    st.sidebar.markdown(
        "<div style='"
        "margin-top: 1rem;"
        "padding-top: 1rem;"
        "border-top: 1px solid #334155;"
        "'>"
        f"<span style='font-size: 0.88em; font-weight: 600; color: #f8fafc;'>👤 {st.session_state.get('observer_name', 'User')}</span><br>"
        f"<span style='font-size: 0.70em; color: #cbd5e1; letter-spacing: 0.03em; text-transform: lowercase;'>version {get_app_version()}</span><br><br>"
        "</div>",
        unsafe_allow_html=True,
    )
    
    # Render the consolidated Shift End button
    from utils.bootstrap import render_custom_sidebar
    render_custom_sidebar()

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
    pages.append(st.Page("vault_views/8_Help.py", title="Help"))

pg = st.navigation(pages)
pg.run()
