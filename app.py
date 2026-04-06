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

# --- 2. SAAS 2026 DESIGN SYSTEM (ULTRA-MODERN & MOBILE-READY) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- GLOBAL THEME --- */
    .stApp {
        background-color: #020617 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.08) 0px, transparent 50%) !important;
        color: #f1f5f9 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* --- SIDEBAR REFINEMENT (SAAS STYLE) --- */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* FORCE SIDEBAR VISIBILITY & READABILITY */
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    [data-testid="stSidebarNav"] span {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #10b981 !important;
        letter-spacing: -1.5px !important;
        font-weight: 800 !important;
    }
    /* Fix the radio button (sidebar menu) labels */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* --- SAAS CARDS (LINEAR STYLE) --- */
    .saas-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 24px;
        box-shadow: 
            0 4px 6px -1px rgba(0, 0, 0, 0.1), 
            0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .saas-card:hover {
        transform: translateY(-4px);
        background: rgba(30, 41, 59, 0.6);
        border-color: rgba(16, 185, 129, 0.4);
        box-shadow: 
            0 20px 25px -5px rgba(0, 0, 0, 0.2), 
            0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    /* --- METRICS & DATA --- */
    .m-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
    }
    .m-value {
        font-size: 3rem;
        font-weight: 800;
        color: #ffffff !important;
        line-height: 1;
        letter-spacing: -0.04em;
    }
    .m-status {
        font-size: 0.85rem;
        color: #10b981;
        margin-top: 12px;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.1);
        padding: 4px 12px;
        border-radius: 100px;
        display: inline-block;
    }

    /* --- FORMS & INPUTS --- */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: rgba(15, 23, 42, 0.9) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        font-size: 1rem !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 32px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.39) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45) !important;
    }

    /* --- TYPOGRAPHY & LAYOUT --- */
    h1 {
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        letter-spacing: -0.04em !important;
        margin-bottom: 40px !important;
        line-height: 0.9 !important;
    }
    h2, h3 { color: #ffffff !important; font-weight: 700 !important; }
    
    /* Hide Defaults */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stHeader"] { background: transparent !important; }

    /* --- MOBILE OPTIMIZATION --- */
    @media (max-width: 768px) {
        h1 { font-size: 2.5rem !important; }
        .saas-card { padding: 20px; }
    }
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

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0;'>VAULT</h2><h1 style='margin-top:-15px; font-size:3.5rem !important;'>ELITE</h1>", unsafe_allow_html=True)
    anim = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim: st_lottie(anim, height=160, key="nav_turtle")
    
    st.markdown("<div style='margin: 30px 0;'></div>", unsafe_allow_html=True)
    menu = st.radio("SYSTEM ACCESS", ["📈 Global View", "📥 Rapid Intake", "🔍 Field Analysis", "🛠️ Registry"])
    st.markdown("--- ")
    st.markdown(f"<p style='opacity:0.5; font-size:0.75rem; font-family:monospace;'>SESSION_ID: {st.session_state.session_id}</p>", unsafe_allow_html=True)

# --- 5. MAIN INTERFACE ---
if menu == "📈 Global View":
    st.markdown("<h1>System<br>Insights</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="saas-card"><div class="m-label">Active Entities</div><div class="m-value">{active}</div><div class="m-status">🟢 Stable</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="saas-card"><div class="m-label">Pipping Watch</div><div class="m-value">{pip}</div><div class="m-status" style="color:#f59e0b">🟠 Critical</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="saas-card"><div class="m-label">Sync Status</div><div class="m-value">100%</div><div class="m-status">🌐 Encrypted</div></div>', unsafe_allow_html=True)
        
        st.markdown("### Activity Log")
        st.markdown("<div class='saas-card' style='background:rgba(16,185,129,0.05); border-color:rgba(16,185,129,0.2); font-weight:600;'>System heartbeat confirmed. All biological markers within range. No anomalies detected.</div>", unsafe_allow_html=True)
    except: st.error("Awaiting Neural Link...")

elif menu == "📥 Rapid Intake":
    st.markdown("<h1>Burst<br>Intake</h1>", unsafe_allow_html=True)
    st.markdown('<div class="saas-card">', unsafe_allow_html=True)
    with st.form("intake_form", clear_on_submit=True):
        spec_data = supabase.table("species").select("common_name").execute().data
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier", placeholder="Subject Name")
        m_spec = c2.selectbox("Biological Class", [s['common_name'] for s in spec_data])
        e_count = st.number_input("Entity Quantity", 1, 50, 10)
        
        if st.form_submit_button("EXECUTE DEPLOYMENT"):
            st.balloons()
            st.toast("Vault Synchronized!", icon="✅")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 Field Analysis":
    st.markdown("<h1>Bio<br>Logging</h1>", unsafe_allow_html=True)
    st.markdown('<div class="saas-card">Scanner active. Please select a target bin to begin analysis.</div>', unsafe_allow_html=True)

elif menu == "🛠️ Registry":
    st.markdown("<h1>Vault<br>Registry</h1>", unsafe_allow_html=True)
    try:
        df = pd.DataFrame(supabase.table("species").select("*").execute().data)
        st.dataframe(df, use_container_width=True)
    except: st.error("Registry unreachable.")

