import streamlit as st
import os
import pandas as pd
import requests
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

# --- 2. GLOBAL HIGH-CONTRAST CSS (FIXED FOR VISIBILITY) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&family=JetBrains+Mono:wght@500&display=swap');

    /* Force App Background */
    .stApp {
        background-color: #020617 !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    /* --- SIDEBAR TEXT VISIBILITY FIX --- */
    /* Forces ALL sidebar text, labels, and icons to be pure white and bold */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    [data-testid="stSidebarNav"] span, 
    [data-testid="stSidebar"] label p, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }

    /* --- BUTTON CONTRAST FIX --- */
    /* Force Emerald background and White text to prevent white-on-white */
    .stButton > button {
        background-color: #10b981 !important;
        color: #ffffff !important;
        border: 2px solid #059669 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        height: 65px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
    }
    .stButton > button:hover {
        background-color: #059669 !important;
        transform: translateY(-2px);
    }

    /* --- INPUT READABILITY --- */
    [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }

    /* Hide Defaults */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. CORE LOGIC ---
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

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown("<h3 style='margin-bottom:0; color:white;'>INCUBATOR</h3><h1 style='margin-top:-10px; font-weight:800; font-size:3.2rem !important; color:white;'>VAULT</h1>", unsafe_allow_html=True)
    anim_data = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim_data: st_lottie(anim_data, height=140, key="nav_anim")
    
    menu = st.radio("SYSTEM CORE", ["📊 DASHBOARD", "🐣 NEW INTAKE", "🔍 FIELD LOG", "🛠️ REGISTRY"])

# --- 5. VIEWS ---
if menu == "📊 DASHBOARD":
    st.markdown("<h1>System Insights</h1>", unsafe_allow_html=True)
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Active Entities", active)
        with c2: st.metric("Pipping Phase", pip)
        with c3: st.metric("Sync Status", "100%")

        # ALERTS: FIXED SCHEMA - Using harvest_date from bin as created_at is missing from egg table
        st.subheader("🚨 Biological Alerts")
        threshold_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        # Fetch eggs where the linked bin's harvest_date is older than 60 days
        late_eggs = supabase.table("egg").select("egg_id, bin(mother(mother_name), harvest_date)").eq("current_stage", "Mature").execute().data
        
        alerts_found = False
        if late_eggs:
            for egg in late_eggs:
                h_date = egg['bin']['harvest_date'] if egg.get('bin') else None
                if h_date and h_date < threshold_date:
                    m_name = egg['bin']['mother']['mother_name'] if egg['bin'].get('mother') else "Unknown"
                    st.warning(f"⚠️ CRITICAL: Egg {egg['egg_id']} ({m_name}) overdue since {h_date}.")
                    alerts_found = True
        
        if not alerts_found:
            st.success("✓ Biological markers stable.")

    except Exception as e: st.error(f"Database Error: {e}")

elif menu == "🐣 NEW INTAKE":
    st.markdown("<h1>New Intake</h1>", unsafe_allow_html=True)
    
    with st.form("intake_form", clear_on_submit=True):
        species_data = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in species_data}
        
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier (Mother)", placeholder="e.g. Shelly")
        m_spec = c2.selectbox("Biological Class", list(spec_map.keys()))
        e_count = st.number_input("Entity Quantity", 1, 100, 10)
        
        if st.form_submit_button("SAVE INTAKE & REGISTER EGGS"):
            try:
                # 1. Mother
                mother_res = supabase.table("mother").select("mother_id").eq("mother_name", m_name).execute()
                mother_id = mother_res.data[0]['mother_id'] if mother_res.data else \
                            supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec]}).execute().data[0]['mother_id']
                
                # 2. Bin
                bin_id = supabase.table("bin").insert({"mother_id": mother_id, "total_eggs": e_count, "harvest_date": datetime.now().strftime('%Y-%m-%d')}).execute().data[0]['bin_id']
                
                # 3. Eggs
                egg_batch = [{"bin_id": bin_id, "current_stage": "Incubating", "status": "Active"} for _ in range(int(e_count))]
                supabase.table("egg").insert(egg_batch).execute()
                
                st.balloons()
                st.success(f"Saved {e_count} eggs for {m_name}.")
            except Exception as e: st.error(f"Save Failed: {e}")

elif menu == "🔍 FIELD LOG":
    st.markdown("<h1>Field Analysis</h1>", unsafe_allow_html=True)

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Database Registry</h1>", unsafe_allow_html=True)
    data = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(data, use_container_width=True)

