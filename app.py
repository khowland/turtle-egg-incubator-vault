"""
=============================================================================
Module:     app.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Main entry point and home page for the Vault Elite app.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
from utils.session import render_sidebar
from utils.css import BASE_CSS

# Configure Page
st.set_page_config(
    page_title="Vault Elite Pro",
    page_icon="🐢",
    layout="wide"
)

# Inject Design System
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# Main Home Content
st.markdown("<h1>Neural Nexus Home</h1>", unsafe_allow_html=True)
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.markdown("""
### 🧪 Program Status
Welcome to the **Wildlife In Need Center (WINC)** turtle egg management system.

**Mission Status:** Phase A (Observation Engine) is active.

**Instructions:**
1. Select your name in the sidebar.
2. Navigate to **Observations** to log data.
""")
st.markdown("</div>", unsafe_allow_html=True)

if not st.session_state.get("logged_in"):
    st.info("💡 Please identify yourself in the sidebar to begin logging data.")
