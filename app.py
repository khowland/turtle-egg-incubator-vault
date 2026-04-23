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
# Prefers .jpg (opaque background) over .png (transparent) — CR-20260423
_assets_dir = Path(__file__).parent / "assets"
_logo_path = next(
    (p for p in [_assets_dir / "winc-logo2.jpg", _assets_dir / "winc-logo2.png"] if p.exists()),
    None
)
if _logo_path:
    st.logo(str(_logo_path))

# --- Bottom sidebar: user identity + version + SHIFT END ---
# NOTE: With st.navigation(), ALL st.sidebar.* content appears BELOW nav links
# regardless of call order. This is Streamlit's intended behaviour.
# The spacer below pushes the identity block visually away from the last nav item
# (~3 invisible menu-item heights + horizontal rule) per CR-20260423.
if st.session_state.get("observer_id"):
    st.sidebar.markdown(
        "<div style='"
        "margin-top: 7rem;"
        "padding-top: 0.75rem;"
        "border-top: 1px solid #334155;"
        "'>"
        f"<span style='font-size: 0.88em; font-weight: 600; color: #e2e8f0;'>👤 {st.session_state.get('observer_name', 'User')}</span><br>"
        f"<span style='font-size: 0.70em; color: #475569; letter-spacing: 0.03em;'>{VERSION}</span>"
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
