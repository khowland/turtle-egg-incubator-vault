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
        st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("views/intake.py", title="New Intake", icon="🐣"),
        st.Page("views/observations.py", title="Observations", icon="🔍"),
        st.Page("views/settings.py", title="Settings", icon="⚙️"),
        st.Page("views/reports.py", title="Reports", icon="📈")
    ])
    # Display user info briefly at top of sidebar
    st.sidebar.caption(f"👤 {st.session_state.get('observer_name')}")
    if st.sidebar.button("Log Out"): 
        st.session_state.observer_id = None
        st.rerun()
    pg.run()
