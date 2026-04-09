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

st.set_page_config(page_title="Login | WINC", page_icon="🐢", layout="wide")

if 'global_font_size' not in st.session_state:
    st.session_state.global_font_size = 18

st.markdown(f"<style>p, div, label, span, .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb='select'] {{ font-size: {st.session_state.global_font_size}px !important; }} [data-testid='stHeader'] {{ visibility: hidden; }}</style>", unsafe_allow_html=True)

show_splash_screen()
