import streamlit as st
from utils.session import render_custom_sidebar
from utils.css import BASE_CSS

st.set_page_config(page_title="Dashboard | WINC", page_icon="📊", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)
render_custom_sidebar()

st.title("📊 Biological Dashboard")
st.info("Welcome to the WINC Incubator Vault Dashboard.")
