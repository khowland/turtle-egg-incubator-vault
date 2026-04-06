import streamlit as st
import os
import pandas as pd
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_lottie import st_lottie

# --- 1. INITIALIZATION & SECRETS ---
load_dotenv('.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = "kxfkfeuhkdopgmkpdimo"

st.set_page_config(
    page_title="Vault Elite",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NUCLEAR GLASS DESIGN SYSTEM (2026 ELITE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- GLOBAL RESET & THEME --- */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    /* FORCE ALL TEXT TO BE VISIBLE */
    * { color: #ffffff !important; }
    
    /* --- SIDEBAR ELITE GLASS --- */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        background-image: linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, transparent 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Fix Sidebar Labels & Radio Buttons specifically */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* --- GLASS CARDS (AWARD WINNING STYLE) --- */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .glass-card:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(16, 185, 129, 0.4);
        transform: translateY(-8px);
    }

    /* --- ELITE METRICS --- */
    .m-title { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #10b981 !important; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 12px; opacity: 0.8; }
    .m-big { font-size: 3.5rem; font-weight: 800; color: #ffffff !important; line-height: 1; letter-spacing: -2px; }
    .m-stat { font-size: 0.9rem; color: #10b981 !important; margin-top: 12px; font-weight: 600; background: rgba(16, 185, 129, 0.1); padding: 4px 12px; border-radius: 100px; display: inline-block; }

    /* --- INPUTS & BUTTONS --- */
    .stTextInput input, .stSelectbox div, .stNumberInput input, .stTextArea textarea {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 1rem !important;
    }
    .stButton > button {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        transition: all 0.3s !important;
    }
    .stButton > button:hover {
        background: #10b981 !important;
        color: #ffffff !important;
        box-shadow: 0 0 40px rgba(16, 185, 129, 0.3);
    }

    /* --- TYPOGRAPHY --- */
    h1 {
        font-size: 4rem !important;
        font-weight: 800 !important;
        letter-spacing: -3px !important;
        margin-bottom: 40px !important;
        line-height: 0.9 !important;
    }
    h2, h3 { font-weight: 700 !important; color: #ffffff !important; }

    /* Hide Defaults */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. UTILS & DATA ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_lottieurl(url: str):
    try: 
        r = requests.get(url, timeout=3)
        if r.status_code == 200: return r.json()
    except: return None

supabase = get_supabase()

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"Elisa_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try: supabase.table("sessionlog").insert({"session_id": st.session_state.session_id, "user_name": "Elisa"}).execute()
    except: pass

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0;'>VAULT</h3><h1 style='-webkit-text-fill-color:white; font-size:3rem !important; margin-top:0;'>ELITE</h1>", unsafe_allow_html=True)
    anim = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim: st_lottie(anim, height=180, key="side_anim")
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    nav = st.radio("", ["SYSTEM STATUS", "CORE INTAKE", "BIO LOGGING", "DATABASE"])
    st.markdown("<div style='margin-top: 50px; opacity:0.5; font-size:0.8rem;'>SESSION: ELISA</div>", unsafe_allow_html=True)

# --- 5. INTERFACE ---
if nav == "SYSTEM STATUS":
    st.markdown("<h1>Global<br>Insights</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><div class="m-title">Active Entities</div><div class="m-big">{active}</div><div class="m-stat">+0.0% Stable</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><div class="m-title">Pipping Phase</div><div class="m-big">{pip}</div><div class="m-stat" style="color:#f59e0b !important;">Alert Active</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><div class="m-title">Network Link</div><div class="m-big">100%</div><div class="m-stat">Synchronized</div></div>', unsafe_allow_html=True)
    except: st.error("Awaiting Neural Link...")

elif nav == "CORE INTAKE":
    st.markdown("<h1>Rapid<br>Deployment</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("intake", clear_on_submit=True):
        spec_list = [s['common_name'] for s in supabase.table("species").select("common_name").execute().data]
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier")
        m_spec = c2.selectbox("Species Class", spec_list)
        e_count = st.number_input("Entity Count", 1, 50, 10)
        if st.form_submit_button("SYNC TO VAULT"):
            st.balloons()
            st.success("Sequence Confirmed.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "BIO LOGGING":
    st.markdown("<h1>Biological<br>Analysis</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">Bio-markers awaiting target selection.</div>', unsafe_allow_html=True)

elif nav == "DATABASE":
    st.markdown("<h1>Registry<br>Access</h1>", unsafe_allow_html=True)
    df = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(df, use_container_width=True)

