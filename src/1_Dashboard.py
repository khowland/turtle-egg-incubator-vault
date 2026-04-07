import streamlit as st
import plotly.express as px
import pandas as pd

st.title("📊 Biological Dashboard")
st.subheader("Incubation Progress")
chart_data = pd.DataFrame({
    'Stage': ['Intake', 'Developing', 'Vascular', 'Mature', 'Pipping', 'Hatched'],
    'Count': [12, 45, 30, 8, 2, 55]
})
fig = px.bar(chart_data, x='Stage', y='Count', color='Stage')
st.plotly_chart(fig, use_container_width=True)
