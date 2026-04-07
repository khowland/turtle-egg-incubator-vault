import streamlit as st
from utils.db import get_supabase

def init_session():
    if 'observer_id' not in st.session_state: st.session_state.observer_id = None
    if 'env_synced' not in st.session_state: st.session_state.env_synced = False

def show_splash_screen():
    st.markdown("<div style='text-align: center; padding: 50px;'><h1 style='color: #10B981;'>🐢 WINC Incubator Vault</h1><p style='color: #94A3B8;'>Please select your name to begin the session</p></div>", unsafe_allow_html=True)
    supabase = get_supabase()
    observers = supabase.table('observer').select('*').eq('is_active', True).execute().data
    cols = st.columns([1, 2, 1])
    with cols[1]:
        with st.form("login_form"):
            options = {f"{o['display_name']} ({o['role']})": o['id'] for o in observers}
            selected = st.selectbox("Observer Identity", options=list(options.keys()))
            if st.form_submit_button("Launch Vault", use_container_width=True):
                st.session_state.observer_id = options[selected]
                st.session_state.observer_name = selected.split(' (')[0]
                st.rerun()

def render_custom_sidebar():
    """Helper to show user info and logout at the top of the sidebar without breaking nav."""
    st.sidebar.markdown(f"### 👤 {st.session_state.get('observer_name', 'User')}")
    if st.sidebar.button("Log Out"):
        st.session_state.observer_id = None
        st.rerun()
    st.sidebar.divider()
