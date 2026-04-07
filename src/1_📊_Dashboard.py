"""
=============================================================================
Module:     src/1_📊_Dashboard.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    High-level biological overview and alerts.
=============================================================================
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from utils.session import render_custom_sidebar
from utils.css import BASE_CSS
from utils.db import get_supabase

st.set_page_config(page_title="Dashboard | WINC", page_icon="📊", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_custom_sidebar()

st.title("📊 Biological Dashboard")

# --- MOCK DATA FOR POC ---
st.subheader("Incubation Progress")
chart_data = pd.DataFrame({
    'Stage': ['Intake', 'Developing', 'Vascular', 'Mature', 'Pipping', 'Hatched'],
    'Count': [12, 45, 30, 8, 2, 55]
})
fig = px.bar(chart_data, x='Stage', y='Count', color='Stage', 
             color_discrete_sequence=px.colors.qualitative.Antique)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.warning("🔔 8 Eggs are currently in 'Mature' stage and nearing pip window.")
with col2:
    st.info("💡 Average incubation temp this week: 84.2°F")
