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
show_splash_screen()
