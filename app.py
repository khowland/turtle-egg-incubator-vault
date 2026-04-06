import streamlit as st
import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_lottie import st_lottie

# --- 1. CONFIGURATION ---
load_dotenv('.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

st.set_page_config(
    page_title="Vault Elite 2026",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LEAD UI/UX DESIGN SYSTEM (SAAS ELITE 2026) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Base Reset & Deep Space Palette */
    .stApp {
        background-color: #020617 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.12) 0px, transparent 50%) !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* --- SIDEBAR ELITE GLASS (MOBILE OPTIMIZED) --- */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.8) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        width: 350px !important;
    }
    /* Force Sidebar Visibility & Contrast */
    [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] label p, [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    /* CRITICAL FIX: Ensure sidebar toggle is visible when minimized */
    [data-testid="stHeader"] {
        background: transparent !important;
        color: #ffffff !important;
    }
    [data-testid="stHeader"] button {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid #10b981 !important;
        border-radius: 12px !important;
        color: #10b981 !important;
        scale: 1.2;
    }

    /* --- ELITE DEPTH CARDS (NON-FLAT) --- */
    .elite-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.3), 
            0 0 30px rgba(16, 185, 129, 0.05);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .elite-card:hover {
        background: rgba(30, 41, 59, 0.65);
        border-color: rgba(16, 185, 129, 0.5);
        transform: translateY(-8px);
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.4), 0 0 50px rgba(16, 185, 129, 0.15);
    }

    /* --- METRICS & BIOLOGICAL DATA --- */
    .m-label { font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #10b981 !important; text-transform: uppercase; letter-spacing: 2.5px; margin-bottom: 12px; }
    .m-value { font-size: 3.8rem; font-weight: 800; color: #ffffff !important; letter-spacing: -0.04em; line-height: 1; }
    .m-status { font-size: 0.95rem; color: #ffffff !important; margin-top: 15px; background: rgba(16, 185, 129, 0.2); padding: 6px 18px; border-radius: 100px; display: inline-block; font-weight: 700; border: 1px solid #10b981; }

    /* --- WET-HAND MOBILE CONTROLS --- */
    .stTextInput input, .stSelectbox div, .stNumberInput input, .stTextArea textarea {
        background-color: #05080c !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        padding: 18px 24px !important;
        font-size: 1.1rem !important;
        height: 64px !important;
    }
    .stButton > button {
        background: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 24px 48px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        width: 100% !important;
        height: 75px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: 0 10px 30px rgba(255, 255, 255, 0.15) !important;
    }
    .stButton > button:hover {
        transform: scale(1.025);
        background: #10b981 !important;
        color: #ffffff !important;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.4) !important;
    }
    .stButton > button p { color: inherit !important; }

    /* --- BIOLOGICAL GUARDRAIL ALERT (PULSING RED) --- */
    @keyframes pulse-red-glow {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); border-color: rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); border-color: rgba(239, 68, 68, 1); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); border-color: rgba(239, 68, 68, 0.4); }
    }
    .critical-bio-alert {
        border: 2px solid #ef4444 !important;
        background: rgba(239, 68, 68, 0.15) !important;
        animation: pulse-red-glow 2s infinite;
    }

    /* Hide Defaults but keep Header (for sidebar toggle) */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. CORE LOGIC & SUPABASE ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = get_supabase()

def load_lottieurl(url: str):
    try: 
        r = requests.get(url, timeout=3)
        if r.status_code == 200: return r.json()
    except: return None

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"Elisa_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0; letter-spacing: 2px;'>INCUBATOR</h3><h1 style='margin-top:-10px; font-weight:800; font-size:4rem !important;'>VAULT</h1>", unsafe_allow_html=True)
    anim_data = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim_data: st_lottie(anim_data, height=180, key="nav_anim")
    else: st.markdown("<h1 style='text-align:center;'>🐢</h1>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)
    menu = st.radio("SYSTEM CORE", ["📊 DASHBOARD", "🐣 RAPID INTAKE", "🔍 FIELD LOG", "🛠️ REGISTRY"])
    st.markdown("<div style='margin-top:100px; opacity:0.3; font-size:0.75rem; font-family:monospace;'>VAULT-ELITE-PRO-2026</div>", unsafe_allow_html=True)

# --- 5. APP VIEWS ---
if menu == "📊 DASHBOARD":
    st.markdown("<h1>System<br>Insights</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="elite-card"><div class="m-label">Active Entities</div><div class="m-value">{active}</div><div class="m-status">STABLE</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="elite-card"><div class="m-label">Pipping Phase</div><div class="m-value">{pip}</div><div class="m-status" style="color:#f59e0b !important;">PHASE CRITICAL</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="elite-card"><div class="m-label">Neural Link</div><div class="m-value">100%</div><div class="m-status">SYNCED</div></div>', unsafe_allow_html=True)

        # BIOLOGICAL GUARDRAILS
        st.subheader("🚨 Biological Alerts")
        threshold_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S')
        late_eggs = supabase.table("egg").select("egg_id, mother(mother_name)").eq("current_stage", "Mature").lt("created_at", threshold_date).execute().data
        
        if late_eggs:
            for egg in late_eggs:
                st.markdown(f'<div class="elite-card critical-bio-alert">⚠️ <b>CRITICAL:</b> Egg <b>{egg["egg_id"]}</b> ({egg["mother"]["mother_name"]}) has exceeded the 60-day Mature stage window. Bio-assessment required.</div>', unsafe_allow_html=True)
        else:
            st.markdown("<div class='elite-card' style='border-color: #10b981; color: #10b981;'>✓ All biological indicators are within stable range.</div>", unsafe_allow_html=True)
            
        # SPECIES PROGRESS
        st.subheader("⏳ Developmental Progress")
        active_eggs = supabase.table("egg").select("egg_id, created_at, current_stage").eq("status", "Active").limit(5).execute().data
        for egg in active_eggs:
            # Calculate days elapsed since created_at
            days_in = (datetime.now() - datetime.fromisoformat(egg['created_at'].split('+')[0])).days
            progress = min(days_in / 75.0, 1.0) # Assume 75-day target
            st.markdown(f"**Egg ID:** `{egg['egg_id']}` ({egg['current_stage']})")
            st.progress(progress)
            st.markdown(f"<p style='font-size:0.8rem; opacity:0.6;'>{days_in} / 75 Days Incubated</p>", unsafe_allow_html=True)

    except Exception as e: st.error(f"Awaiting Neural Uplink... {e}")

elif menu == "🐣 RAPID INTAKE":
    st.markdown("<h1>New Entity<br>Registration</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">', unsafe_allow_html=True)
    with st.form("intake", clear_on_submit=True):
        specs = [s['common_name'] for s in supabase.table("species").select("common_name").execute().data]
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier (Mother)", placeholder="Shelly")
        m_spec = c2.selectbox("Biological Class", specs)
        e_count = st.number_input("Entity Quantity", 1, 50, 10)
        if st.form_submit_button("EXECUTE DEPLOYMENT"):
            st.balloons()
            st.success("Sequence Confirmed.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 FIELD LOG":
    st.markdown("<h1>Field<br>Analysis</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">Scanner active. Please select a bin to begin biological marker logging.</div>', unsafe_allow_html=True)

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Core<br>Registry</h1>", unsafe_allow_html=True)
    data = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(data, use_container_width=True)

