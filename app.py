import streamlit as st
from utils.session import init_session, show_splash_screen, render_custom_sidebar
from utils.css import BASE_CSS

st.set_page_config(
    page_title="WINC Incubator Vault",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Surgical Aero-Shield CSS
st.markdown(BASE_CSS, unsafe_allow_html=True)

init_session()

if not st.session_state.get('observer_id'):
    show_splash_screen()
else:
    # Define authorized pages with standard paths for Windows stability
    pages = {
        "WINC INCUBATOR VAULT": [
            st.Page("src/1_Dashboard.py", title="Dashboard", icon="📊")
        ],
        "Field Operations": [
            st.Page("src/2_New_Intake.py", title="New Intake", icon="🐣"),
            st.Page("src/3_Observations.py", title="Observations", icon="🔍")
        ],
        "System": [
            st.Page("src/5_Settings.py", title="Settings", icon="⚙️"),
            st.Page("src/6_Reports.py", title="Reports", icon="📈")
        ]
    }
    
    pg = st.navigation(pages)
    render_custom_sidebar()
    pg.run()
