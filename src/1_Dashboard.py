import streamlit as st
import plotly.express as px
import pandas as pd

# User Header
col1, col2 = st.columns([4, 1])
col1.title("📊 Biological Dashboard")
if col2.button("Log Out", use_container_width=True):
    st.session_state.observer_id = None
    st.rerun()
st.caption(f"👤 Observer: {st.session_state.get('observer_name', 'Staff')}")
st.divider()

st.subheader("Incubation Progress")
chart_data = pd.DataFrame({
    'Stage': ['Intake', 'Developing', 'Vascular', 'Mature', 'Pipping', 'Hatched'],
    'Count': [12, 45, 30, 8, 2, 55]
})
fig = px.bar(chart_data, x='Stage', y='Count', color='Stage')
st.plotly_chart(fig, use_container_width=True)
