"""
=============================================================================
Module:     app.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Main entry point with automated cache management and sidebar.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""
import streamlit as st
from utils.session import render_sidebar
from utils.css import BASE_CSS

st.set_page_config(page_title="Vault Elite Pro", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# The sidebar now handles observer selection and auto-syncing
render_sidebar()

st.markdown("<h1>Vault Elite: Neural Nexus</h1>", unsafe_allow_html=True)
st.markdown("""
<div class='glass-card'>
    <h3>System Operational</h3>
    <p>Welcome to the <b>WINC Incubator Vault</b>. Use the sidebar to navigate 
    between Intake, Observations, and System Analytics.</p>
    <p><i>Note: The system now uses <b>Autonomous Syncing</b>. Data refreshes 
    automatically after every save.</i></p>
</div>
""", unsafe_allow_html=True)
