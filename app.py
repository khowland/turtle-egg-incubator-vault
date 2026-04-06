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
    page_title="Incubator Vault 2026",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THEME & DESIGN SYSTEM (2026 EDITION) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-deep-navy: #0a0f1e;
        --emerald-glow: #10b981;
        --emerald-muted: rgba(16, 185, 129, 0.2);
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
        --text-main: #e2e8f0;
    }

    .stApp {
        background: linear-gradient(-45deg, #050810, #0a1622, #061a1a, #0a0f1e);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: var(--text-main);
        font-family: 'Inter', sans-serif;
    }

    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: rgba(16, 185, 129, 0.05);
        border-left: 4px solid var(--emerald-glow);
        padding: 1.5rem;
        border-radius: 16px;
        backdrop-filter: blur(8px);
    }

    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--emerald-glow);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
    }

    .stButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }

    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
    }

    h1, h2, h3 {
        background: linear-gradient(to right, #ffffff, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        font-weight: 800 !important;
    }

    .stSidebar { background: rgba(5, 8, 16, 0.95) !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. UTILS & DATA ---
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200: return r.json()
    except: return None

def wake_up_supabase():
    headers = {"Authorization": f"Bearer {SUPABASE_MGMT_TOKEN}"}
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/unpause"
    try: requests.get(SUPABASE_URL, timeout=1)
    except:
        with st.status("✨ Synchronizing Vault...", expanded=True) as status:
            resp = requests.post(url, headers=headers)
            if resp.status_code in [200, 201, 409]:
                time.sleep(25)
                st.rerun()

# --- 4. SESSION & NAV ---
if 'session_id' not in st.session_state:
    user = "Elisa"
    sid = f"{user}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.session_id, st.session_state.user_name = sid, user
    try:
        get_supabase().table("sessionlog").insert({"session_id": sid, "user_name": user, "user_agent": "Vault-2026-X"}).execute()
    except: pass

supabase = get_supabase()

# Sidebar
lottie_url = "https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json"
lottie_data = load_lottieurl(lottie_url)

with st.sidebar:
    st.markdown("### 🐢 VAULT CORE")
    if lottie_data: st_lottie(lottie_data, height=120, key="sidebar_anim")
    st.write(f"**Observer:** `{st.session_state.user_name}`")
    menu = st.radio("SYSTEM ACCESS", ["📊 Insights", "📥 Batch Intake", "🔍 Field Observation", "🛠️ Settings"])

# --- 5. PAGES ---
if menu == "📊 Insights":
    st.title("📈 System Insights")
    wake_up_supabase()
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count
        pipping = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><div class="metric-label">Live Eggs</div><div class="metric-value">{active or 0}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-label">Pipping Watch</div><div class="metric-value">{pipping or 0}</div></div>', unsafe_allow_html=True)
        c3.markdown('<div class="metric-card"><div class="metric-label">Vault Integrity</div><div class="metric-value">100%</div></div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("🚨 Critical Alerts")
        alerts = supabase.table("eggobservation").select("egg_id, molding, leaking, timestamp").or_("molding.eq.true,leaking.eq.true").order("timestamp", desc=True).limit(5).execute()
        if alerts.data: st.table(alerts.data)
        else: st.success("Vault status: Stable.")
    except: st.info("Awaiting data stream...")

elif menu == "📥 Batch Intake":
    st.title("📥 Batch Intake")
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.form("intake", border=False):
            spec_list = supabase.table("species").select("species_id, common_name").execute().data
            spec_map = {s['common_name']: s['species_id'] for s in spec_list}
            
            m_name = st.text_input("Mother Name", placeholder="Shelly")
            m_spec = st.selectbox("Species", options=list(spec_map.keys()))
            e_count = st.number_input("Egg Count", 1, 100, 10)
            if st.form_submit_button("INITIATE SEQUENCE"):
                try:
                    mid = supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec], "created_by_session": st.session_state.session_id}).execute().data[0]['mother_id']
                    bid = supabase.table("bin").insert({"mother_id": mid, "total_eggs": e_count, "created_by_session": st.session_state.session_id}).execute().data[0]['bin_id']
                    eggs = [{"bin_id": bid, "created_by_session": st.session_state.session_id} for _ in range(e_count)]
                    supabase.table("egg").insert(eggs).execute()
                    st.balloons()
                    st.success(f"Batch {bid} registered.")
                except Exception as e: st.error(f"Sequence Failed: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 Field Observation":
    st.title("🔍 Field Observation")
    bins = [b['bin_id'] for b in supabase.table("bin").select("bin_id").execute().data]
    sel_bin = st.selectbox("Target Bin", bins, index=None)
    if sel_bin:
        egg_list = [e['egg_id'] for e in supabase.table("egg").select("egg_id").eq("bin_id", sel_bin).execute().data]
        sel_eggs = st.multiselect("Target Eggs", egg_list)
        if sel_eggs:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            with st.form("obs", border=False):
                c1, c2 = st.columns(2)
                v = c1.checkbox("Vascularity")
                m = c2.checkbox("Molding")
                l = c1.checkbox("Leaking")
                ch = c2.slider("Chalking", 0, 2, 0)
                stg = st.selectbox("Stage", ["Developing", "Established", "Mature", "Pipping", "Hatched"])
                if st.form_submit_button("SYNC DATA"):
                    obs = [{"egg_id": eid, "vascularity": v, "molding": m, "leaking": l, "chalking": ch, "session_id": st.session_state.session_id} for eid in sel_eggs]
                    supabase.table("eggobservation").insert(obs).execute()
                    for eid in sel_eggs: supabase.table("egg").update({"current_stage": stg}).eq("egg_id", eid).execute()
                    st.toast("Data Synchronized!", icon="✅")
            st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛠️ Settings":
    st.title("🛠️ Core Settings")
    data = supabase.table("species").select("*").execute().data
    st.dataframe(pd.DataFrame(data))

st.sidebar.divider()
if st.sidebar.button("📦 EXPORT VAULT DATA"):
    try:
        df = pd.DataFrame(supabase.table("eggobservation").select("*").execute().data)
        st.sidebar.download_button("DOWNLOAD CSV", df.to_csv(index=False), f"vault_{datetime.now().strftime('%Y%m%d')}.csv")
    except: st.sidebar.error("Export error.")
