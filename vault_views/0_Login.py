"""
=============================================================================
Module:        vault_views/0_Login.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.session
Inputs:        None
Outputs:       st.session_state (observer_id, session_id)
Description:   Session Gateway and Splash Screen.
=============================================================================
"""
import streamlit as st
from utils.session import show_splash_screen

if 'global_font_size' not in st.session_state:
    st.session_state.global_font_size = 18

st.markdown(f"""
    <style>
        .stApp {{ font-family: 'Inter', sans-serif; }}
        [data-testid='stHeader'] {{ background: transparent !important; opacity: 0.8; }}
    </style>
""", unsafe_allow_html=True)

show_splash_screen()
