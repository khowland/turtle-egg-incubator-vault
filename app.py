import streamlit as st
from utils.session import init_session, show_splash_screen

st.set_page_config(page_title="WINC Vault", page_icon="🐢", layout="wide")
init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    pg = st.navigation([
        st.Page("navigation/1_Dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("navigation/2_New_Intake.py", title="New Intake", icon="🐣"),
        st.Page("navigation/3_Observations.py", title="Observations", icon="🔍"),
        st.Page("navigation/5_Settings.py", title="Settings", icon="⚙️"),
        st.Page("navigation/6_Reports.py", title="Reports", icon="📈")
    ])
    pg.run()
