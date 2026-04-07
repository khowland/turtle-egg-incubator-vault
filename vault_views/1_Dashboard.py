import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title='Dashboard | WINC', page_icon='📊', layout='wide')

# Header
col1, col2 = st.columns([4, 1])
col1.title("📊 Biological Dashboard")
if col2.button("🚪 Log Out", width='stretch'):
    st.session_state.observer_id = None
    st.rerun()
st.caption(f"👤 Observer: {st.session_state.get('observer_name', 'Staff')}")
st.divider()

# Mock Data for Analytics (until DB is populated)
st.subheader("📈 Incubation Progress")
data = pd.DataFrame({
    'Stage': ['Intake', 'Developing', 'Vascular', 'Mature', 'Pipping', 'Hatched'],
    'Count': [15, 38, 22, 10, 3, 45]
})
fig = px.bar(data, x='Stage', y='Count', color='Stage', 
             color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig, width='stretch')

# Metrics Row
m1, m2, m3 = st.columns(3)
m1.metric("Total Eggs in Vault", "133", "+12")
m2.metric("Mature (Alert!)", "10", "-2")
m3.metric("Incubation Success", "92%", "+1%")
