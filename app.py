import streamlit as st
from utils.session import init_session, show_splash_screen
from utils.css import BASE_CSS

st.set_page_config(page_title="WINC Vault", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    # Using a flat list for max compatibility on Windows
    pages = [
        st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("views/intake.py", title="New Intake", icon="🐣"),
        st.Page("views/observations.py", title="Observations", icon="🔍"),
        st.Page("views/settings.py", title="Settings", icon="⚙️"),
        st.Page("views/reports.py", title="Reports", icon="📈")
    ]
    pg = st.navigation(pages)
    pg.run()
