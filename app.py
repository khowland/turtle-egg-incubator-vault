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

    /* --- FORCED READABILITY FOR LABELS (FIXED) --- */
    /* This ensures all labels and form descriptions are white and visible */
    [data-testid="stWidgetLabel"] p, label, .stMarkdown p {
        color: #ffffff !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* --- SIDEBAR ELITE GLASS --- */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 10, 10, 0.8) !important;
        backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Header & Toggle Visibility */
    [data-testid="stHeader"] {
        background: transparent !important;
        color: #ffffff !important;
    }

    /* --- ELITE DEPTH CARDS --- */
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
    }

    /* --- INPUTS & DROPDOWNS (FIXED ARTIFACTS) --- */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #05080c !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        height: 60px !important;
    }
    /* Ensure dropdown menu items are readable */
    div[data-baseweb="popover"] li { color: #000000 !important; }

    /* --- PRIMARY BUTTON (FIXED VISIBILITY) --- */
    /* Set to Emerald background with White text for maximum contrast */
    .stButton > button {
        background: #10b981 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 18px !important;
        padding: 20px 40px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100% !important;
        height: 70px !important;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 15px 30px rgba(16, 185, 129, 0.5) !important;
    }

    /* Pulse Animation for Critical Alerts */
    @keyframes pulse-red-glow {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
        70% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .critical-bio-alert { border: 2px solid #ef4444 !important; animation: pulse-red-glow 2s infinite; }

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
    st.markdown("<h3 style='margin-bottom:0; color:white;'>INCUBATOR</h3><h1 style='margin-top:-10px; font-weight:800; font-size:3.5rem !important; color:white;'>VAULT</h1>", unsafe_allow_html=True)
    anim_data = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim_data: st_lottie(anim_data, height=150, key="nav_anim")
    
    menu = st.radio("SYSTEM CORE", ["📊 DASHBOARD", "🐣 NEW INTAKE", "🔍 FIELD LOG", "🛠️ REGISTRY"])

# --- 5. VIEWS ---
if menu == "📊 DASHBOARD":
    st.markdown("<h1>System<br>Insights</h1>", unsafe_allow_html=True)
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="elite-card"><b>ACTIVE ENTITIES</b><br><span style="font-size:3rem;">{active}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="elite-card"><b>PIPPING PHASE</b><br><span style="font-size:3rem;">{pip}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="elite-card"><b>NEURAL LINK</b><br><span style="font-size:3rem;">100%</span></div>', unsafe_allow_html=True)

        # ALERTS
        st.subheader("🚨 Biological Alerts")
        threshold = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%dT%H:%M:%S')
        late_eggs = supabase.table("egg").select("egg_id, bin(mother(mother_name))").eq("current_stage", "Mature").lt("created_at", threshold).execute().data
        
        if late_eggs:
            for egg in late_eggs:
                m_name = egg['bin']['mother']['mother_name'] if egg.get('bin') else "Unknown"
                st.markdown(f'<div class="elite-card critical-bio-alert">⚠️ <b>CRITICAL:</b> Egg {egg["egg_id"]} ({m_name}) overdue.</div>', unsafe_allow_html=True)
        else:
            st.success("✓ All systems within biological parameters.")

    except Exception as e: st.error(f"Stream Offline: {e}")

elif menu == "🐣 NEW INTAKE":
    # UI UPDATE: Renamed title for clarity
    st.markdown("<h1>New Intake</h1>", unsafe_allow_html=True)
    st.markdown('<div class="elite-card">', unsafe_allow_html=True)
    
    with st.form("intake_form", clear_on_submit=True):
        # Fetch biological classes from DB
        species_data = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in species_data}
        
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Origin Identifier (Mother)", placeholder="e.g. Shelly")
        m_spec = c2.selectbox("Biological Class", list(spec_map.keys()))
        e_count = st.number_input("Entity Quantity", 1, 100, 10)
        
        # UI UPDATE: Action-oriented button label and high-contrast styling via CSS
        if st.form_submit_button("SAVE INTAKE & REGISTER EGGS"):
            try:
                # 1. Handle Mother Record
                mother_res = supabase.table("mother").select("mother_id").eq("mother_name", m_name).execute()
                if mother_res.data:
                    mother_id = mother_res.data[0]['mother_id']
                else:
                    new_mother = supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec]}).execute()
                    mother_id = new_mother.data[0]['mother_id']
                
                # 2. Create Bin
                new_bin = supabase.table("bin").insert({"mother_id": mother_id, "total_eggs": e_count, "harvest_date": datetime.now().strftime('%Y-%m-%d')}).execute()
                bin_id = new_bin.data[0]['bin_id']
                
                # 3. Register Eggs
                egg_batch = [{"bin_id": bin_id, "current_stage": "Incubating", "status": "Active"} for _ in range(int(e_count))]
                supabase.table("egg").insert(egg_batch).execute()
                
                st.balloons()
                st.success(f"Successfully registered {e_count} entities for {m_name}.")
            except Exception as e:
                st.error(f"Intake Failure: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔍 FIELD LOG":
    st.markdown("<h1>Field Analysis</h1>", unsafe_allow_html=True)
    st.info("Awaiting scanner link...")

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Database Registry</h1>", unsafe_allow_html=True)
    data = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(data, use_container_width=True)

