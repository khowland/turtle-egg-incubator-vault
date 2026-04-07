import streamlit as st
from utils.session import init_session, show_splash_screen
from utils.css import BASE_CSS

st.set_page_config(page_title="WINC Vault", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    pg = st.navigation([
        st.Page("src/1_Dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("src/2_New_Intake.py", title="New Intake", icon="🐣"),
        st.Page("src/3_Observations.py", title="Observations", icon="🔍"),
        st.Page("src/5_Settings.py", title="Settings", icon="⚙️"),
        st.Page("src/6_Reports.py", title="Reports", icon="📈")
    ])
    pg.run()
