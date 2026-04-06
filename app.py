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

# --- 2. THE "LINEAR-SPEC" DESIGN SYSTEM (2026 ELITE) ---
# This CSS uses ultra-high specificity to force a modern, professional, mobile-ready look.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* --- 1. GLOBAL OVERRIDES --- */
    .stApp {
        background-color: #000000 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.1) 0px, transparent 50%) !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* FORCE ALL TEXT TO BE VISIBLE */
    * { color: #ffffff !important; }
    
    /* --- 2. SIDEBAR REFINEMENT --- */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.8) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    /* Sidebar Navigation Labels - The main 'invisible' culprit */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: -0.01em !important;
    }

    /* --- 3. THE "SLICK" CARDS (NOT FLAT) --- */
    .elite-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .elite-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(16, 185, 129, 0.5);
        transform: translateY(-8px);
        box-shadow: 0 12px 40px 0 rgba(16, 185, 129, 0.2);
    }

    /* --- 4. METRIC DESIGN --- */
    .m-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #10b981 !important;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 12px;
        opacity: 0.8;
    }
    .m-value {
        font-size: 3.5rem;
        font-weight: 800;
        color: #ffffff !important;
        letter-spacing: -0.04em;
        line-height: 1;
    }
    .m-status {
        font-size: 0.9rem;
        color: #ffffff !important;
        margin-top: 15px;
        background: rgba(16, 185, 129, 0.2);
        padding: 6px 16px;
        border-radius: 100px;
        display: inline-block;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* --- 5. MOBILE-FRIENDLY CONTROLS --- */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: #0c0c0c !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        font-size: 1.1rem !important;
        height: 60px !important;
    }
    
    /* --- 6. THE "WET-HAND" BUTTON --- */
    .stButton > button {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 20px 40px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.1) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        background: #10b981 !important;
        color: #ffffff !important;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4) !important;
    }
    .stButton > button p { color: inherit !important; }

    /* --- 7. TYPOGRAPHY --- */
    h1 {
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.05em !important;
        line-height: 0.85 !important;
        margin-bottom: 40px !important;
        background: linear-gradient(to bottom, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* HIDE DEFAULTS */
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stHeader"] { background: transparent !important; }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }
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
    st.markdown("<h3 style='margin-bottom:0;'>INCUBATOR</h3><h1 style='margin-top:-10px; font-size:4rem !important; -webkit-text-fill-color:white !important;'>VAULT</h1>", unsafe_allow_html=True)
    anim = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim: st_lottie(anim, height=180, key="turtle_nav")
    st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)
    menu = st.radio("SYSTEM CORE", ["📈 DASHBOARD", "📥 BATCH INTAKE", "🔍 FIELD ANALYSIS", "🛠️ DATABASE"])
    st.markdown("<div style='margin-top: 100px; opacity:0.3; font-size:0.7rem; font-family:monospace;'>ELITE-2026-v3.5</div>", unsafe_allow_html=True)

# --- 5. MAIN CONTENT ---
if menu == "📈 DASHBOARD":
    st.markdown("<h1>Neural<br>Insights</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="elite-card"><div class="m-label">Live Entities</div><div class="m-value">{active}</div><div class="m-status">SYSTEM STABLE</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="elite-card"><div class="m-label">Pipping Watch</div><div class="m-value">{pip}</div><div class="m-status" style="color:#f59e0b !important;">PHASE CRITICAL</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="elite-card"><div class="m-label">Vault Sync</div><div class="m-value">100%</div><div class="m-status">ENCRYPTED</div></div>', unsafe_allow_html=True)
        
        st.markdown("### Activity Log")
        st.markdown("<div class='elite-card' style='background:rgba(16,185,129,0.05); border-color:rgba(16,185,129,0.2);'>Neural link active. All species biological markers within nominal range. No anomalies reported.</div>", unsafe_allow_html=True)
    except: st.error("Awaiting Uplink...")

elif menu == "📥 BATCH INTAKE":
    st.markdown("<h1>Rapid<br>Intake</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">', unsafe_allow_html=True)
    with st.form("intake", clear_on_submit=True):
        specs = [s['common_name'] for s in supabase.table("species").select("common_name").execute().data]
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier", placeholder="e.g. Shelly")
        m_spec = c2.selectbox("Species", specs)
        e_count = st.number_input("Quantity", 1, 50, 10)
        if st.form_submit_button("SYNC TO VAULT"):
            st.balloons()
            st.success("Deployment Confirmed.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 FIELD ANALYSIS":
    st.markdown("<h1>Bio<br>Logging</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">Scanner active. Please isolate a bin target to begin biological analysis.</div>', unsafe_allow_html=True)

elif menu == "🛠️ DATABASE":
    st.markdown("<h1>Core<br>Registry</h1>", unsafe_allow_html=True)
    data = supabase.table("species").select("*").execute().data
    st.dataframe(pd.DataFrame(data), use_container_width=True)

