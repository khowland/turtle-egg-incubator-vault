import streamlit as st
from utils.session import init_session, show_splash_screen
from utils.css import BASE_CSS

# Global App Config
st.set_page_config(page_title="WINC Vault", page_icon="🐢", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    # Define Navigation (No categorical headers for max Windows/Browser compatibility)
    pages = [
        st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True),
        st.Page("views/intake.py", title="New Intake", icon="🐣"),
        st.Page("views/observations.py", title="Observations", icon="🔍"),
        st.Page("views/settings.py", title="Settings", icon="⚙️"),
        st.Page("views/reports.py", title="Reports", icon="📈")
    ]
    
    pg = st.navigation(pages)
    
    # IMPORTANT: We do NOT use st.sidebar here to prevent wiping the navigation menu.
    # User info and Logout are now handled inside each page or at the top of the app.
    pg.run()
