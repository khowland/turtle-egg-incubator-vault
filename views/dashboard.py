import streamlit as st
col1, col2 = st.columns([4, 1])
col1.title("📊 Biological Dashboard")
if col2.button("Log Out", key="logout_dash", use_container_width=True): 
    st.session_state.observer_id = None
    st.rerun()
st.caption(f"👤 Observer: {st.session_state.get('observer_name', 'Staff')}")
st.divider()
st.info("Welcome to the WINC Vault Dashboard.")
