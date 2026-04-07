import streamlit as st

st.title("🔍 Observation Engine")
if 'env_synced' not in st.session_state: st.session_state.env_synced = False

if not st.session_state.env_synced:
    st.markdown("### 🌡️ Environment Check-In")
    with st.container(border=True):
        temp = st.number_input("Temp (°F)", value=84.5)
        hum = st.number_input("Humidity (%)", value=80.0)
        if st.button("✅ Sync Environment", use_container_width=True):
            st.session_state.env_synced = True
            st.rerun()
else:
    st.success(f"Session Active | {st.session_state.get('observer_name')}")
    if st.button("Edit Metrics"): st.session_state.env_synced = False; st.rerun()
    st.divider()
    st.info("Multi-Select Egg Grid Placeholder")
