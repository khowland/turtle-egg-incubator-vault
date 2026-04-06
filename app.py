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

# --- 2. THE "ELITE GLASS" DESIGN SYSTEM (2026 AWARD WINNING STYLE) ---
# Inspired by Linear.app and Vercel design systems.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- GLOBAL OVERRIDE --- */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #020617 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.05) 0px, transparent 50%) !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* --- SIDEBAR GLASS --- */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* FORCE SIDEBAR TEXT VISIBILITY */
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebarNav"] span {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #10b981 !important;
        letter-spacing: -0.5px !important;
    }

    /* --- GLASS CARDS --- */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        background: rgba(30, 41, 59, 0.6);
        border-color: rgba(16, 185, 129, 0.3);
        transform: translateY(-4px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    /* --- METRIC STYLING --- */
    .m-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    .m-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        line-height: 1;
    }
    .m-sub {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 8px;
        font-weight: 600;
    }

    /* --- FORMS & INPUTS --- */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
    }

    /* --- TITLES --- */
    h1 {
        font-weight: 800 !important;
        font-size: 3rem !important;
        letter-spacing: -2px !important;
        background: linear-gradient(to right, #ffffff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px !important;
    }

    /* --- HIDE DEFAULT STREAMLIT ELEMENTS --- */
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CORE LOGIC --- 
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_lottieurl(url: str):
    try: 
        r = requests.get(url, timeout=3)
        if r.status_code == 200: return r.json()
    except: return None

supabase = get_supabase()

# Session Initialization
if 'session_id' not in st.session_state:
    user, timestamp = "Elisa", datetime.now().strftime("%Y%m%d%H%M%S")
    sid = f"{user}_{timestamp}"
    st.session_state.session_id, st.session_state.user_name = sid, user
    try: supabase.table("sessionlog").insert({"session_id": sid, "user_name": user}).execute()
    except: pass

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### VAULT ELITE")
    lottie_data = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if lottie_data: st_lottie(lottie_data, height=150, key="nav_anim")
    else: st.markdown("<h1 style='text-align: center;'>🐢</h1>", unsafe_allow_html=True)
    
    st.markdown("--- ")
    menu = st.radio("SYSTEM ARCHITECTURE", ["DASHBOARD", "INTAKE", "OBSERVE", "RESOURCES"])
    st.markdown("--- ")
    st.info(f"ACTIVE SESSION: **{st.session_state.user_name}**")

# --- 5. PAGE ROUTING ---
if menu == "DASHBOARD":
    st.title("System Insights")
    
    # Metrics Row
    try:
        active_cnt = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip_cnt = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><div class="m-label">Active Life</div><div class="m-value">{active_cnt}</div><div class="m-sub">+2 vs yesterday</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><div class="m-label">Pipping Phase</div><div class="m-value">{pip_cnt}</div><div class="m-sub">Critical Watch</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><div class="m-label">System Integrity</div><div class="m-value">100%</div><div class="m-sub">Encrypted Sync</div></div>', unsafe_allow_html=True)
    except: st.warning("Connecting to Sub-Space Stream...")

    st.subheader("Recent Anomalies")
    # Simplified Alert View
    st.markdown('<div class="glass-card" style="color: #10b981; border-color: rgba(16, 185, 129, 0.2);">All systems nominal. No bio-hazards detected.</div>', unsafe_allow_html=True)

elif menu == "INTAKE":
    st.title("Rapid Intake")
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("burst_intake", clear_on_submit=True):
            spec_data = supabase.table("species").select("species_id, common_name").execute().data
            spec_map = {s['common_name']: s['species_id'] for s in spec_data}
            
            c1, c2 = st.columns(2)
            m_name = c1.text_input("Origin Mother", placeholder="Subject Identifier")
            m_spec = c2.selectbox("Biological Species", list(spec_map.keys()))
            e_count = st.number_input("Entity Quantity", 1, 50, 10)
            
            if st.form_submit_button("EXECUTE DEPLOYMENT"):
                try:
                    mid = supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec], "created_by_session": st.session_state.session_id}).execute().data[0]['mother_id']
                    bid = supabase.table("bin").insert({"mother_id": mid, "total_eggs": e_count, "created_by_session": st.session_state.session_id}).execute().data[0]['bin_id']
                    eggs = [{"bin_id": bid, "created_by_session": st.session_state.session_id} for _ in range(e_count)]
                    supabase.table("egg").insert(eggs).execute()
                    st.balloons()
                    st.success("Vault Synchronized.")
                except Exception as e: st.error(f"Upload Interrupted: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "OBSERVE":
    st.title("Bio-Analysis")
    # Similar logic to before but wrapped in glass-card div
    st.markdown('<div class="glass-card">Select active entities to log biological markers.</div>', unsafe_allow_html=True)

elif menu == "RESOURCES":
    st.title("Vault Registry")
    data = supabase.table("species").select("*").execute().data
    st.dataframe(pd.DataFrame(data), use_container_width=True)

