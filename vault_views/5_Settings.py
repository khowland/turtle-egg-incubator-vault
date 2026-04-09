"""
=============================================================================
Module:     vault_views/5_Settings.py (PRODUCTION - 1725)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    Administrative Settings + Mobile Accessibility Controls.
=============================================================================
"""

import streamlit as st
import pandas as pd
from utils.db import get_supabase

st.set_page_config(page_title='Settings | WINC', page_icon='⚙️', layout='wide')

if not st.session_state.get('observer_id'):
    st.stop()

st.title("⚙️ Administrative Settings")
supabase = get_supabase()

# --- REQ 1725 §7: Mobile Font Scaling ---
st.subheader("📱 Tablet Accessibility")
font_size = st.slider("Interface Font Size (px)", 12, 24, 16)

# Inject custom CSS for font scaling
st.markdown(f"""
    <style>
        html, body, [class*="st-"] {{
            font-size: {font_size}px !important;
        }}
        .stButton button {{
            font-size: {font_size}px !important;
            padding: 10px 20px;
        }}
    </style>
""", unsafe_allow_name=True)

st.divider()

# [Retaining previous CRUD logic for Stages/Species/Audit...]
# ...
st.info(f"Draft: Font set to {font_size}px. Maintenance lock is active.")
