import streamlit as st
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_lottie import st_lottie

# --- 1. CORE CONFIGURATION ---
load_dotenv('.env')
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
VERSION = "v5.3 - ROBUST DATA"

st.set_page_config(
    page_title=f"Vault Elite {VERSION}",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. TITANIUM CSS OVERRIDES ---
st.markdown("""
<style>
    .stApp { background-color: #020617 !important; color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #050810 !important; border-right: 1px solid rgba(255, 255, 255, 0.1) !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #FFFFFF !important; font-weight: 800 !important; }
    div.stButton > button { background-color: #10B981 !important; color: #FFFFFF !important; font-weight: 900 !important; border-radius: 12px !important; height: 60px !important; width: 100% !important; }
    div.stButton > button p { color: #FFFFFF !important; font-size: 1.1rem !important; }
    .glass-card { background: rgba(30, 41, 59, 0.55); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 24px; margin-bottom: 20px; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE ACCESS ---
@st.cache_resource
def get_supabase() -> Client: return create_client(SUPABASE_URL, SUPABASE_KEY)
supabase = get_supabase()

def load_lottie(url: str):
    try: return requests.get(url, timeout=3).json()
    except: return None

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"Elisa_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown(f"<div style='color:#10B981; font-weight:bold; font-size:0.9rem; text-align:center; padding:8px; border:2px solid #10B981; border-radius:10px;'>BUILD: {VERSION}</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:white; font-size:3rem; margin-bottom:0;'>VAULT</h1>", unsafe_allow_html=True)
    menu = st.radio("SYSTEM ACCESS", ["📊 DASHBOARD", "🐣 NEW INTAKE", "🔍 OBSERVATIONS", "🛠️ REGISTRY"])
    if st.button("🔄 NEURAL REFRESH"): st.cache_resource.clear(); st.rerun()
    st.caption(f"ID: {st.session_state.session_id}")

# --- 5. VIEWS ---
if menu == "📊 DASHBOARD":
    st.markdown("<h1>Dashboard</h1>", unsafe_allow_html=True)
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><b>ACTIVE</b><br><span style="font-size:2rem;">{active}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><b>PIPPING</b><br><span style="font-size:2rem;">{pip}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><b>STATUS</b><br><span style="font-size:2rem;">STABLE</span></div>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Dashboard Error: {e}")

elif menu == "🐣 NEW INTAKE":
    st.markdown("<h1>New Intake</h1>", unsafe_allow_html=True)
    with st.form("intake_v53", clear_on_submit=True):
        species_data = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in species_data}
        m_name = st.text_input("Mother Name", placeholder="e.g. Shelly")
        m_spec = st.selectbox("Species", list(spec_map.keys()))
        qty = st.number_input("Egg Count", 1, 100, 10)
        if st.form_submit_button("SAVE INTAKE & REGISTER EGGS"):
            try:
                m_res = supabase.table("mother").select("mother_id").eq("mother_name", m_name).execute()
                m_id = m_res.data[0]['mother_id'] if m_res.data else supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec]}).execute().data[0]['mother_id']
                b_id = supabase.table("bin").insert({"mother_id": m_id, "total_eggs": qty, "harvest_date": datetime.now().strftime('%Y-%m-%d')}).execute().data[0]['bin_id']
                batch = [{"bin_id": b_id, "current_stage": "Incubating", "status": "Active"} for _ in range(int(qty))]
                supabase.table("egg").insert(batch).execute()
                st.balloons(); st.success(f"Registered {qty} eggs.")
            except Exception as e: st.error(f"Intake Failure: {e}")

elif menu == "🔍 OBSERVATIONS":
    st.markdown("<h1>Observations</h1>", unsafe_allow_html=True)
    try:
        res = supabase.table("egg").select("egg_id, current_stage, bin(harvest_date, mother(mother_name))").order("egg_id", desc=True).execute()
        if res.data:
            flat = [{"ID": r['egg_id'], "Mother": r.get('bin', {}).get('mother', {}).get('mother_name', 'N/A'), "Stage": r['current_stage'], "Harvested": r.get('bin', {}).get('harvest_date', 'N/A')} for r in res.data]
            st.dataframe(pd.DataFrame(flat), use_container_width=True, hide_index=True)
        else: st.info("No observations registered in vault.")
    except Exception as e: st.error(f"Observation Error: {e}")

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Registry</h1>", unsafe_allow_html=True)
    try:
        res = supabase.table("species").select("*").execute()
        if res.data: st.dataframe(pd.DataFrame(res.data), use_container_width=True, hide_index=True)
        else: st.info("Registry is empty.")
    except Exception as e: st.error(f"Registry Error: {e}")

