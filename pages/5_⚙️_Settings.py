"""
=============================================================================
Module:     pages/5_⚙️_Settings.py
Project:    WINC Incubator Vault v6.3
Purpose:    Administrative settings for species, observers, and system config.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06
=============================================================================
"""

import streamlit as st
from utils.session import render_sidebar
from utils.css import BASE_CSS

st.set_page_config(page_title="Settings | WINC", page_icon="⚙️", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_sidebar()

st.title('⚙️ Settings')
st.info('🚧 Admin Registry CRUD management (Species, Observers) is being finalized for the next sub-release.')
