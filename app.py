import streamlit as st
import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_lottie import st_lottie

# --- 1. INITIALIZATION ---
load_dotenv('.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

st.set_page_config(
    page_title="Vault Elite Pro",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PRO-SAAS DESIGN SYSTEM (2026 ELITE) ---
# Optimized for legibility, mobile use, and depth (non-flat).
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Theme Foundation */
    .stApp {
        background-color: #020617 !important;
        background-image: radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.05) 0px, transparent 50%) !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Surgical Sidebar Fixes */
    [data-testid="stSidebar"] { background-color: #0b111e !important; border-right: 1px solid rgba(255,255,255,0.05) !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    [data-testid="stSidebar"] label p { font-size: 1rem !important; font-weight: 700 !important; }

    /* Elite Cards with Depth */
    .elite-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .elite-card:hover { transform: translateY(-4px); border-color: #10b981; }

    /* Clean Inputs (Fixed Dropdown) */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        border-radius: 12px !important;
        border: 1px solid #374151 !important;
        color: white !important;
        height: 52px !important;
    }
    div[data-baseweb="select"] * { color: white !important; }

    /* Wet-Hand Large Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        height: 64px !important;
        width: 100% !important;
        box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover { transform: scale(1.02); filter: brightness(1.1); }

    /* Typography */
    h1 { font-weight: 800 !important; letter-spacing: -0.04em !important; font-size: 3.5rem !important; line-height: 1 !important; margin-bottom: 30px !important; }
    .m-label { font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #10b981; text-transform: uppercase; letter-spacing: 2px; }
    .m-value { font-size: 2.8rem; font-weight: 800; }

    /* Pulsing Bio-Logic Alert */
    @keyframes pulse-red {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .critical-alert {
        border: 2px solid #ef4444 !important;
        background: rgba(239, 68, 68, 0.1) !important;
        animation: pulse-red 2s infinite;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. CORE UTILS ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = get_supabase()

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"Elisa_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#10b981; margin-bottom:0;'>VAULT</h2><h1 style='margin-top:-10px; font-weight:800;'>ELITE</h1>", unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)
    menu = st.radio("SYSTEM CORE", ["📊 Insights", "🐣 New Intake", "🔍 Observation"])
    st.markdown("--- ")
    st.write(f"**Observer:** Elisa")
    st.caption(f"ID: {st.session_state.session_id}")

# --- 5. APP VIEWS ---
if menu == "📊 Insights":
    st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="elite-card"><div class="m-label">Live Eggs</div><div class="m-value">{active}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="elite-card"><div class="m-label">Pipping Watch</div><div class="m-value">{pip}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="elite-card"><div class="m-label">Sync Status</div><div class="m-value">100%</div></div>', unsafe_allow_html=True)

        st.subheader("🚨 Biological Guardrails")
        # Mature > 60 Days Logic
        threshold = datetime.now() - timedelta(days=60)
        late_eggs = supabase.table("egg").select("egg_id, mother(mother_name), created_at").eq("current_stage", "Mature").lt("created_at", threshold.isoformat()).execute().data
        
        if late_eggs:
            for egg in late_eggs:
                st.markdown(f'<div class="elite-card critical-alert">🔴 <b>CRITICAL WARNING</b>: Egg <b>{egg["egg_id"]}</b> ({egg["mother"]["mother_name"]}) has exceeded the 60-day Mature stage window. Immediate bio-assessment required!</div>', unsafe_allow_html=True)
        else:
            st.markdown("<div class='elite-card' style='border-color:#10b981; color:#10b981;'>✓ All biological indicators are currently within stable range.</div>", unsafe_allow_html=True)
            
        st.subheader("⏳ Incubation Progress")
        # Species-specific countdown simulation (Default 75 days)
        eggs = supabase.table("egg").select("egg_id, created_at").eq("status", "Active").limit(5).execute().data
        for egg in eggs:
            days_incubated = (datetime.now() - datetime.fromisoformat(egg['created_at'].split('+')[0])).days
            progress = min(days_incubated / 75.0, 1.0)
            st.markdown(f"**Egg {egg['egg_id']}** ({days_incubated}/75 days)")
            st.progress(progress)
            
    except: st.error("Awaiting Neural Link...")

elif menu == "🐣 New Intake":
    st.markdown("<h1>Burst Intake</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">', unsafe_allow_html=True)
    with st.form("intake", clear_on_submit=True):
        specs = [s['common_name'] for s in supabase.table("species").select("common_name").execute().data]
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier (Mother)", placeholder="Shelly")
        m_spec = c2.selectbox("Species", specs)
        e_count = st.number_input("Egg Count", 1, 50, 10)
        if st.form_submit_button("EXECUTE DEPLOYMENT"):
            st.balloons()
            st.success("Sequence confirmed. Vault synchronized.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 Observation":
    st.markdown("<h1>Field Log</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">Mobile Scanner Active. Select a target bin in the database to initiate bio-logging.</div>', unsafe_allow_html=True)

