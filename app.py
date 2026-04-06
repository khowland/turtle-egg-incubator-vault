import streamlit as st
import os
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_lottie import st_lottie

# --- 1. CONFIG ---
load_dotenv('.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
PROJECT_REF = "kxfkfeuhkdopgmkpdimo"

st.set_page_config(page_title="Vault Elite", page_icon="🐢", layout="wide")

# --- 2. PROFESSIONAL 2026 DESIGN SYSTEM (FIXED & FUNCTIONAL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Base Theme */
    .stApp { background-color: #030712; color: #f8fafc; font-family: 'Plus Jakarta Sans', sans-serif; }
    
    /* Clean Glass Cards (No Breakage) */
    .vault-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    /* Fix Sidebar Labels */
    [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] label p, [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Fix Inputs & Buttons (No White Blocks) */
    .stTextInput input, .stSelectbox div, .stNumberInput input {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100% !important;
        height: 50px !important;
    }

    /* Metric Styling */
    .m-label { font-family: 'JetBrains Mono'; font-size: 0.7rem; color: #10b981; letter-spacing: 1px; }
    .m-value { font-size: 2.2rem; font-weight: 800; }

    /* Warning Animation */
    @keyframes pulse-red {
        0% { border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { border-color: rgba(239, 68, 68, 1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { border-color: rgba(239, 68, 68, 0.4); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .warning-card { border: 2px solid #ef4444; animation: pulse-red 2s infinite; }

    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. UTILS ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = get_supabase()

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"Elisa_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# --- 4. INTERFACE ---
with st.sidebar:
    st.title("🐢 Vault Elite")
    menu = st.radio("SYSTEM ACCESS", ["📈 Insights", "📥 Intake", "🔍 Observation", "🛠️ Registry"])
    st.info(f"Observer: Elisa\nSession: {st.session_state.session_id}")

if menu == "📈 Insights":
    st.title("System Insights")
    c1, c2, c3 = st.columns(3)
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        with c1: st.markdown(f'<div class="vault-card"><div class="m-label">Live Eggs</div><div class="m-value">{active}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="vault-card"><div class="m-label">Pipping</div><div class="m-value">{pip}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="vault-card"><div class="m-label">Vault Health</div><div class="m-value">100%</div></div>', unsafe_allow_html=True)

        # BIOLOGICAL GUARDRAILS
        st.subheader("🚨 Biological Guardrails")
        # Mature eggs > 60 days warning
        threshold = datetime.now() - timedelta(days=60)
        late_eggs = supabase.table("egg").select("egg_id, mother(mother_name), created_at").eq("current_stage", "Mature").lt("created_at", threshold.isoformat()).execute().data
        
        if late_eggs:
            for egg in late_eggs:
                st.markdown(f'<div class="vault-card warning-card">⚠️ CRITICAL: Egg <b>{egg["egg_id"]}</b> (Mother: {egg["mother"]["mother_name"]}) has been in Mature stage for over 60 days!</div>', unsafe_allow_html=True)
        else: st.success("All biological indicators nominal.")
    except: st.error("Awaiting Neural Link...")

elif menu == "📥 Intake":
    st.title("Batch Intake")
    with st.container():
        st.markdown('<div class="vault-card">', unsafe_allow_html=True)
        with st.form("intake", clear_on_submit=True):
            specs = supabase.table("species").select("species_id, common_name").execute().data
            spec_map = {s['common_name']: s['species_id'] for s in specs}
            
            c1, c2 = st.columns(2)
            m_name = c1.text_input("Mother Name", placeholder="Shelly")
            m_spec = c2.selectbox("Species", options=list(spec_map.keys()))
            e_count = st.number_input("Quantity", 1, 100, 10)
            
            if st.form_submit_button("EXECUTE INTAKE"):
                try:
                    mid = supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec], "created_by_session": st.session_state.session_id}).execute().data[0]['mother_id']
                    bid = supabase.table("bin").insert({"mother_id": mid, "total_eggs": e_count, "created_by_session": st.session_state.session_id}).execute().data[0]['bin_id']
                    eggs = [{"bin_id": bid, "created_by_session": st.session_state.session_id} for _ in range(e_count)]
                    supabase.table("egg").insert(eggs).execute()
                    st.balloons()
                    st.success("Vault Synchronized.")
                except Exception as e: st.error(f"Upload Interrupted: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

# ... (Observation and Registry pages simplified for focus on fix)
