import streamlit as st
from utils.session import init_session, show_splash_screen
from utils.css import BASE_CSS

# Entry Configuration
st.set_page_config(page_title="WINC Vault", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    # Using a flat list is the most compatible way to ensure the menu shows on all OS types
    pages = [
        st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("views/intake.py", title="New Intake", icon="🐣"),
        st.Page("views/observations.py", title="Observations", icon="🔍"),
        st.Page("views/settings.py", title="Settings", icon="⚙️"),
        st.Page("views/reports.py", title="Reports", icon="📈")
    ]

    pg = st.navigation(pages)

    # Manual sidebar additions (rendered after navigation to avoid conflict)
    st.sidebar.markdown(f"### 👤 {st.session_state.get('observer_name')}")
    if st.sidebar.button("Log Out", use_container_width=True):
        st.session_state.observer_id = None
        st.rerun()

    pg.run()
