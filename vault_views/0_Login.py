"""
# ==============================================================================
# Module:        vault_views/0_Login.py
# Project:       Incubator Vault v7.2.1
# Client:        Wildlife In Need Center (WINC)
# Author:        Antigravity (Sovereign Sprint)
# Description:   Session Gateway and Splash Screen.
#
# Revision History:
# ------------------------------------------------------------------------------
# Date          Author          Version     Description
# ------------------------------------------------------------------------------
# 2026-04-08    Antigravity     7.2.0       Initial Splash setup
# ==============================================================================
"""
import streamlit as st
from utils.session import show_splash_screen

# st.set_page_config removed v7.9.5 — now handled by app.py

if 'global_font_size' not in st.session_state:
    st.session_state.global_font_size = 18

# Login uses a custom minimal bootstrap as it handles the initial handshake
st.markdown(f"""
    <style>
        .stApp {{ font-family: 'Inter', sans-serif; }}
        /* Ensure toggle visibility */
        [data-testid='stHeader'] {{ background: transparent !important; opacity: 0.8; }}
    </style>
""", unsafe_allow_html=True)

show_splash_screen()
