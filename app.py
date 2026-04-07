import streamlit as st
from utils.session import init_session, show_splash_screen

st.set_page_config(page_title="WINC Vault", page_icon="🐢", layout="wide")
init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    # Minimal navigation list
    pages = [
        st.Page("navigation/1_Dashboard.py", title="Dashboard", icon="📊"),
        st.Page("navigation/2_New_Intake.py", title="New Intake", icon="🐣"),
        st.Page("navigation/3_Observations.py", title="Observations", icon="🔍"),
        st.Page("navigation/5_Settings.py", title="Settings", icon="⚙️"),
        st.Page("navigation/6_Reports.py", title="Reports", icon="📈")
    ]
    pg = st.navigation(pages)
    
    # Manual sidebar user info
    st.sidebar.markdown(f"### 👤 {st.session_state.get('observer_name')}")
    if st.sidebar.button("Log Out"): 
        st.session_state.observer_id = None
        st.rerun()
    st.sidebar.divider()
    
    pg.run()
