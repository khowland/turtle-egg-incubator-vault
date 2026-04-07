"""
=============================================================================
Module:     app.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    Main Entry Point with Splash Login and Navigation Gate.
=============================================================================
"""
import streamlit as st
from utils.session import init_session, show_splash_screen, render_custom_sidebar
from utils.css import BASE_CSS

# Professional Configuration
st.set_page_config(
    page_title="WINC Incubator Vault",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None, 'Report a bug': None, 'About': None}
)

# Inject sanitized Aero-Shield CSS
st.markdown(BASE_CSS, unsafe_allow_html=True)

init_session()

# NAVIGATION LOCK: If not logged in, show ONLY splash screen
if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    # Define authorized pages with explicit Navigation Categories
    pg = st.navigation({
        "WINC INCUBATOR VAULT": [
            st.Page("src/1_📊_Dashboard.py", title="Dashboard", icon="📊")
        ],
        "Field Operations": [
            st.Page("src/2_🐣_New_Intake.py", title="New Intake", icon="🐣"),
            st.Page("src/3_🔍_Observations.py", title="Observations", icon="🔍")
        ],
        "System": [
            st.Page("src/5_⚙️_Settings.py", title="Settings", icon="⚙️"),
            st.Page("src/6_📈_Reports.py", title="Reports", icon="📈")
        ]
    })
    render_custom_sidebar()
    pg.run()
