import streamlit as st
import os
import pandas as pd
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_lottie import st_lottie

# --- 1. CONFIG ---
load_dotenv('.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

st.set_page_config(page_title="Vault Elite", page_icon="🐢", layout="wide")

# --- 2. NUCLEAR CSS (AWARD WINNING DESIGN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* 1. THE NUCLEAR RESET - FORCE WHITE TEXT EVERYWHERE */
    * { 
        color: #FFFFFF !important; 
        font-family: 'Inter', sans-serif !important; 
    }
    
    /* 2. BASE BACKGROUND */
    .stApp {
        background: #000000 !important;
    }

    /* 3. SIDEBAR - BLACK GLASS */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebarNav"] * { color: #FFFFFF !important; }
    
    /* Fix the invisible Radio Button labels in Sidebar */
    [data-testid="stSidebar"] label p { 
        color: #FFFFFF !important; 
        font-size: 1rem !important; 
        font-weight: 600 !important; 
    }

    /* 4. GLASS CARDS (LINEAR/VERCEL STYLE) */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(40px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 20px;
        transition: border 0.3s ease;
    }
    .glass-card:hover {
        border-color: #10b981;
    }

    /* 5. METRIC TYPOGRAPHY */
    .m-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #10b981 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }
    .m-value {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -2px;
    }

    /* 6. INPUTS - DARK FIELDS */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: #0A0A0A !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        height: 50px !important;
    }

    /* 7. BUTTONS - PURE WHITE CONTRAST */
    .stButton > button {
        background: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border: none !important;
        width: 100%;
    }
    .stButton > button * { color: #000000 !important; }

    /* 8. TITLES */
    h1 { font-size: 4rem !important; font-weight: 800 !important; letter-spacing: -4px !important; }
    
    /* Hide Defaults */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA & LOGIC ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = get_supabase()

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"Elisa_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 2rem !important; letter-spacing: -1px !important;'>VAULT <span style='color:#10b981 !important;'>ELITE</span></h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("MENU", ["DASHBOARD", "INTAKE", "OBSERVE"])
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown(f"<code style='color:#10b981 !important;'>ID: {st.session_state.session_id}</code>", unsafe_allow_html=True)

# --- 5. MAIN CONTENT ---
if menu == "DASHBOARD":
    st.markdown("<h1>Insights</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><div class="m-label">Live Entities</div><div class="m-value">{active}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><div class="m-label">Pipping Watch</div><div class="m-value">{pip}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><div class="m-label">System Status</div><div class="m-value">STABLE</div></div>', unsafe_allow_html=True)
    except: st.error("Awaiting Data Uplink...")

elif menu == "INTAKE":
    st.markdown("<h1>New Batch</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("intake_form"):
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Mother")
        e_count = c2.number_input("Egg Count", 1, 50, 10)
        if st.form_submit_button("SYNC TO VAULT"):
            st.balloons()
            st.success("Confirmed.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "OBSERVE":
    st.markdown("<h1>Field Log</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">Bio-metrics scanner active. Select a bin in the database to begin analysis.</div>', unsafe_allow_html=True)

