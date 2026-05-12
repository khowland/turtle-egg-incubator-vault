import os
import time
import streamlit as st

st.set_page_config(
    page_title='WINC Incubator',
    page_icon='🐢',
    layout='wide',
    initial_sidebar_state='expanded'
)

from utils.identity import init_clinical_session

# Sovereign Identity Provider — establishes clinical session and observer context
init_clinical_session()

from utils.bootstrap import bootstrap_page, get_app_version

# Bootstrap Page
bootstrap_page('WINC Incubator', '🐢', render_sidebar=False)

# Sidebar Identity Footer
if st.session_state.get('observer_id'):
    st.sidebar.markdown(
        "<div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #334155;'>"
        f"<span style='font-size: 0.88em; font-weight: 600; color: #f8fafc;'>👤 {st.session_state.get('observer_name', 'User')}</span><br>"
        f"<span style='font-size: 0.70em; color: #cbd5e1; letter-spacing: 0.03em; text-transform: lowercase;'>version {get_app_version()}</span><br><br>"
        "</div>",
        unsafe_allow_html=True,
    )
    from utils.bootstrap import render_custom_sidebar
    render_custom_sidebar()

# Navigation Router
if not st.session_state.get('observer_id'):
    pages = [st.Page('vault_views/0_Login.py', title='Welcome', icon='🐢')]
else:
    pages = [
        st.Page('vault_views/1_Dashboard.py', title='Dashboard', icon='📊'),
        st.Page('vault_views/2_New_Intake.py', title='Intake', icon='🐣'),
        st.Page('vault_views/3_Observations.py', title='Observations', icon='🔍'),
        st.Page('vault_views/5_Settings.py', title='Settings', icon='⚙️'),
        st.Page('vault_views/6_Reports.py', title='Reports', icon='📈'),
        st.Page('vault_views/7_Diagnostic.py', title='System Check', icon='🩺'),
        st.Page('vault_views/8_Help.py', title='Help', icon='📚'),
    ]

pg = st.navigation(pages)
pg.run()