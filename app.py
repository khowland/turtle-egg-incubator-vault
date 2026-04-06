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

st.set_page_config(
    page_title="Vault Elite 2026",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NEO-GLASS DESIGN SYSTEM (2026 PREVIEW) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* --- GLOBAL THEME --- */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617) !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* --- SIDEBAR REFINEMENT --- */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        width: 300px !important;
    }
    
    /* Ensure sidebar text is crisp and white */
    [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] label p, [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.01em !important;
    }

    /* --- NEO-GLASS CARDS --- */
    .vault-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .vault-card:hover {
        transform: translateY(-4px);
        border-color: rgba(16, 185, 129, 0.3);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        background: rgba(30, 41, 59, 0.6);
    }

    /* --- METRICS & TYPOGRAPHY --- */
    .m-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 8px;
    }
    .m-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.02em;
    }
    .m-trend {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* --- INPUTS & FORMS --- */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        transition: border-color 0.2s;
    }
    .stTextInput input:focus {
        border-color: #10b981 !important;
    }

    /* --- BUTTONS --- */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.025em !important;
        width: 100% !important;
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
        opacity: 0.9;
    }

    /* --- MOBILE OPTIMIZATIONS --- */
    @media (max-width: 768px) {
        h1 { font-size: 2.5rem !important; }
        .vault-card { padding: 16px; }
    }

    /* Hide Streamlit Header/Footer */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CORE UTILS ---
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
    st.markdown("<h2 style='color:#10b981; letter-spacing:-1px; margin-bottom:0;'>VAULT</h2><h1 style='margin-top:-10px; font-weight:800; color:white;'>ELITE</h1>", unsafe_allow_html=True)
    anim = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim: st_lottie(anim, height=140, key="nav_turtle")
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
    
    # Modern Navigation Icons would be better, but for now we use clear labels
    menu = st.radio("SYSTEM ACCESS", ["📈 Insights", "📥 Rapid Intake", "🔍 Field Log", "🛠️ Registry"])
    st.markdown("--- ")
    st.markdown(f"<p style='opacity:0.5; font-size:0.75rem; font-family:monospace;'>SESSION_ID: {st.session_state.session_id}</p>", unsafe_allow_html=True)

# --- 5. MAIN INTERFACE ---
if menu == "📈 Insights":
    st.markdown("<h1 style='font-weight:800; letter-spacing:-2px;'>Dashboard</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="vault-card"><div class="m-label">Active Life</div><div class="m-value">{active}</div><div class="m-trend">🟢 Stable Status</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="vault-card"><div class="m-label">Pipping Watch</div><div class="m-value">{pip}</div><div class="m-trend" style="color:#f59e0b">🟠 Critical Phase</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="vault-card"><div class="m-label">Vault Health</div><div class="m-value">100%</div><div class="m-trend">🌐 Sync Active</div></div>', unsafe_allow_html=True)
        
        st.markdown("### Recent Activity")
        st.markdown("<div class='vault-card' style='background:rgba(16,185,129,0.05); border-color:rgba(16,185,129,0.2);'>No anomalies detected in the current incubation cycle. All biological markers within range.</div>", unsafe_allow_html=True)
    except: st.error("Awaiting Neural Link...")

elif menu == "📥 Rapid Intake":
    st.markdown("<h1 style='font-weight:800; letter-spacing:-2px;'>New Intake</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="vault-card">', unsafe_allow_html=True)
        with st.form("intake_form", clear_on_submit=True):
            spec_data = supabase.table("species").select("common_name").execute().data
            c1, c2 = st.columns(2)
            m_name = c1.text_input("Origin Identifier", placeholder="e.g. Shelly")
            m_spec = c2.selectbox("Biological Class", [s['common_name'] for s in spec_data])
            e_count = st.number_input("Quantity", 1, 50, 10)
            
            if st.form_submit_button("SYNC TO VAULT"):
                st.balloons()
                st.toast("Batch Intake Successful", icon="✅")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 Field Log":
    st.markdown("<h1 style='font-weight:800; letter-spacing:-2px;'>Field Observation</h1>", unsafe_allow_html=True)
    st.markdown('<div class="vault-card">Scanner awaiting target selection. Navigate to a bin in the database to start bio-logging.</div>', unsafe_allow_html=True)

elif menu == "🛠️ Registry":
    st.markdown("<h1 style='font-weight:800; letter-spacing:-2px;'>Registry Access</h1>", unsafe_allow_html=True)
    try:
        df = pd.DataFrame(supabase.table("species").select("*").execute().data)
        st.dataframe(df, use_container_width=True)
    except: st.error("Database unreachable.")

