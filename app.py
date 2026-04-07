"""
=============================================================================
Module:     app.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Main entry point. Shows a simple welcome screen with quick
            navigation guidance for non-technical staff.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Simplified for non-technical staff)
=============================================================================
"""

import streamlit as st
from utils.session import render_sidebar
from utils.css import BASE_CSS
from utils.logger import logger

logger.info("🚀 Incubator Vault started.")

st.set_page_config(page_title="Incubator Vault | WINC", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_sidebar()

# --- HOME SCREEN ---
st.markdown("## 🐢 Incubator Vault")
st.markdown("""
<div class='glass-card'>
    <h3>Welcome!</h3>
    <p>Use the <b>sidebar menu</b> (☰ on mobile) to navigate:</p>
    <ul>
        <li>📊 <b>Dashboard</b> — see how the eggs are doing</li>
        <li>🐣 <b>New Intake</b> — register a new mother and eggs</li>
        <li>🔍 <b>Observations</b> — log what you see at the incubator</li>
        <li>🌡️ <b>Environment</b> — record temperature and humidity</li>
        <li>⚙️ <b>Settings</b> — manage species, staff, and incubators</li>
        <li>📈 <b>Reports</b> — season stats and data export</li>
    </ul>
    <p style='color: #94A3B8; font-size: 0.9rem;'>
        Tip: Pick your name in the sidebar before logging anything.
    </p>
</div>
""", unsafe_allow_html=True)
