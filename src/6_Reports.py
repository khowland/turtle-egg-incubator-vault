import streamlit as st

# Page-Level User Header
col1, col2 = st.columns([4, 1])
col1.title("$(basename "$f" .py | sed 's/[0-9]_//')")
if col2.button("Log Out", key="logout_"+"$(basename "$f" .py)", use_container_width=True):
    st.session_state.observer_id = None
    st.rerun()
st.caption(f"👤 Observer: {st.session_state.get('observer_name', 'Staff')}")
st.divider()

st.info("WINC Vault Page: $(basename "$f" .py). [v6.3.3 Stable]")
