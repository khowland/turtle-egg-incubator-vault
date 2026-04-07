import streamlit as st

# User Header
col1, col2 = st.columns([4, 1])
col1.title("🔍 Observation Engine")
if col2.button("Log Out", key="logout_obs", use_container_width=True): 
    st.session_state.observer_id = None
    st.rerun()
st.caption(f"👤 Observer: {st.session_state.get('observer_name', 'Staff')}")
st.divider()

if 'env_synced' not in st.session_state: st.session_state.env_synced = False

if not st.session_state.env_synced:
    st.info("🌡️ Environment Check-In Required")
    temp = st.number_input("Incubator Temp (°F)", value=84.5)
    hum = st.number_input("Incubator Humidity (%)", value=80.0)
    if st.button("✅ Sync & Unlock", use_container_width=True):
        st.session_state.env_synced = True; st.rerun()
else:
    st.success("✅ Session Active | Environment Synced")
    if st.button("Edit Metrics"): st.session_state.env_synced = False; st.rerun()
    st.divider()
    st.write("Multi-Select Egg Grid active...")
