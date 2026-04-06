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
    page_title="Vault 2026",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. HIGH-CONTRAST 2026 THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Base Reset */
    .stApp { background-color: #05080c; color: #ffffff; font-family: 'Inter', sans-serif; }

    /* Fix Sidebar Readability */
    [data-testid="stSidebar"] { background-color: #0b1118 !important; }
    [data-testid="stSidebar"] .st-emotion-cache-16idsys p { color: #ffffff !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] .st-emotion-cache-eqo0zs { color: #ffffff !important; }
    [data-testid="stSidebar"] .st-emotion-cache-16idsys { color: #ffffff !important; }
    [data-testid="stSidebar"] h3 { color: #10b981 !important; }
    [data-testid="stSidebar"] label { color: #ffffff !important; font-weight: 600 !important; }
    
    /* Fix the radio button (sidebar menu) labels */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #ffffff !important; }
    [data-testid="stSidebar"] .st-d6 { color: #ffffff !important; }
    
    /* Clean Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-top: 2px solid #10b981;
        padding: 20px;
        border-radius: 12px;
        text-align: left;
    }
    .metric-label { font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #10b981; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 2.2rem; font-weight: 800; color: #ffffff; margin-top: 5px; }

    /* Modern Headers */
    h1, h2, h3 { color: #ffffff !important; font-weight: 800 !important; margin-bottom: 0.5rem !important; }
    
    /* High Contrast Success/Info */
    .stSuccess { background-color: rgba(16, 185, 129, 0.1) !important; color: #10b981 !important; border: 1px solid #10b981 !important; }
    .stInfo { background-color: rgba(255, 255, 255, 0.05) !important; color: #e2e8f0 !important; }
    
    /* Form Elements Fix */
    .stTextInput input, .stSelectbox div, .stNumberInput input { background-color: #1a222d !important; color: white !important; border: 1px solid #30363d !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. UTILS ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)

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
        with st.status("✨ Initializing Vault...", expanded=True) as status:
            requests.post(url, headers=headers)
            time.sleep(25)
            st.rerun()

# --- 4. SESSION & NAV ---
if 'session_id' not in st.session_state:
    user, timestamp = "Elisa", datetime.now().strftime("%Y%m%d%H%M%S")
    sid = f"{user}_{timestamp}"
    st.session_state.session_id, st.session_state.user_name = sid, user
    try: get_supabase().table("sessionlog").insert({"session_id": sid, "user_name": user, "user_agent": "Vault-2026-v3.3"}).execute()
    except: pass

supabase = get_supabase()

# Sidebar
lottie_url = "https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json"
lottie_data = load_lottieurl(lottie_url)

with st.sidebar:
    st.title("🐢 Vault Core")
    if lottie_data: st_lottie(lottie_data, height=120, key="sidebar_anim")
    st.write(f"**Observer:** `{st.session_state.user_name}`")
    menu = st.radio("SYSTEM ACCESS", ["📈 Insights", "📥 Intake", "🔍 Observation", "🛠️ Settings"])

# --- 5. PAGES ---
if menu == "📈 Insights":
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

elif menu == "📥 Intake":
    st.title("📥 Batch Intake")
    with st.form("intake"):
        spec_list = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in spec_list}
        
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Mother Name", placeholder="Shelly")
        m_spec = c2.selectbox("Species", options=list(spec_map.keys()))
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

elif menu == "🔍 Observation":
    st.title("🔍 Field Observation")
    bins = [b['bin_id'] for b in supabase.table("bin").select("bin_id").execute().data]
    sel_bin = st.selectbox("Target Bin", bins, index=None)
    if sel_bin:
        egg_list = [e['egg_id'] for e in supabase.table("egg").select("egg_id").eq("bin_id", sel_bin).execute().data]
        sel_eggs = st.multiselect("Target Eggs", egg_list)
        if sel_eggs:
            with st.form("obs"):
                c1, c2 = st.columns(2)
                v, m, l = c1.checkbox("Vascularity"), c2.checkbox("Molding"), c1.checkbox("Leaking")
                ch = c2.slider("Chalking", 0, 2, 0)
                stg = st.selectbox("Stage", ["Developing", "Established", "Mature", "Pipping", "Hatched"])
                if st.form_submit_button("SYNC DATA"):
                    obs = [{"egg_id": eid, "vascularity": v, "molding": m, "leaking": l, "chalking": ch, "session_id": st.session_state.session_id} for eid in sel_eggs]
                    supabase.table("eggobservation").insert(obs).execute()
                    for eid in sel_eggs: supabase.table("egg").update({"current_stage": stg}).eq("egg_id", eid).execute()
                    st.toast("Data Synchronized!", icon="✅")

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
