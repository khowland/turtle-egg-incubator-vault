"""
=============================================================================
Module:     app.py
Project:    WINC Incubator Vault v6.3
Purpose:    Main entry & Splash Login Screen. Manages persistent observer 
            sessions and global navigation.
Author:     Agent Zero (Automated Build)
=============================================================================
"""

import streamlit as st
from utils.session import init_session, render_sidebar, show_splash_screen
from utils.css import BASE_CSS
from utils.logger import logger

st.set_page_config(page_title="WINC Incubator Vault", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Initialize session state variables
init_session()

# Check if observer is selected (Splash Screen Logic)
if not st.session_state.get('observer_id'):
    show_splash_screen()
    st.stop() # Halt execution until user "logs in"

# Main App Content (once logged in)
render_sidebar()

st.markdown("## 🐢 WINC Incubator Vault")
st.markdown("""
<div class='glass-card'>
    <h3>Welcome back, """ + st.session_state.get('observer_name', 'User') + """!</h3>
    <p>Your session is active. Navigate using the sidebar:</p>
    <ul>
        <li>📊 <b>Dashboard</b> — Real-time biological KPIs</li>
        <li>🐣 <b>New Intake</b> — 4-Step Registration Wizard</li>
        <li>🔍 <b>Observations</b> — Batch Health Logging (Requires Environment Sync)</li>
    </ul>
</div>
""", unsafe_allow_html=True)
