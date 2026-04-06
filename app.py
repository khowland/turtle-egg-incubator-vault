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
VERSION = "v5.0 - TITANIUM"

st.set_page_config(
    page_title=f"Vault Elite {VERSION}",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NUCLEAR TITANIUM CSS (v5.0) ---
# Using extreme specificity to override Streamlit's Emotion engine.
st.markdown("""
<style>
    /* 1. Global Baseline */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #020617 !important;
        color: #FFFFFF !important;
    }

    /* 2. SIDEBAR - FORCED HIGH CONTRAST */
    [data-testid="stSidebar"] {
        background-color: #050810 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    /* Force ALL text in sidebar to be pure white */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Navigation and Widget Labels specifically */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        opacity: 1 !important;
    }

    /* 3. PRIMARY BUTTON - FORCED EMERALD (FIXES WHITE-ON-WHITE) */
    div.stButton > button {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        border: 2px solid #34D399 !important;
        border-radius: 14px !important;
        font-weight: 900 !important;
        height: 75px !important;
        width: 100% !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4) !important;
    }
    /* Force nested button text to be white and bold */
    div.stButton > button p, div.stButton > button span, div.stButton > button div {
        color: #FFFFFF !important;
        font-size: 1.3rem !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }
    div.stButton > button:hover {
        background-color: #059669 !important;
        border-color: #FFFFFF !important;
        transform: scale(1.01);
    }

    /* 4. FORM FIELD LABELS & INPUTS */
    [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
    }
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
    }

    /* 5. GLASS CARDS */
    .glass-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* Hide default header/footer */
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
    st.markdown(f"<div style='color:#10B981; font-weight:bold; font-size:1.2rem; text-align:center; padding:10px; border:2px solid #10B981; border-radius:10px;'>BUILD: {VERSION}</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:white; font-size:3.5rem; margin-bottom:0;'>VAULT</h1><p style='color:#10B981; font-weight:bold; letter-spacing:4px; margin-top:-10px;'>ELITE PRO</p>", unsafe_allow_html=True)
    anim = load_lottie("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim: st_lottie(anim, height=130, key="nav_anim")
    
    menu = st.radio("SYSTEM ACCESS", ["📊 DASHBOARD", "🐣 NEW INTAKE", "🔍 FIELD LOG", "🛠️ REGISTRY"])
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption(f"ID: {st.session_state.session_id}")

# --- 5. VIEWS ---
if menu == "📊 DASHBOARD":
    st.markdown("<h1>System Insights</h1>", unsafe_allow_html=True)
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><b>ACTIVE EGGS</b><br><span style="font-size:3rem; font-weight:bold;">{active}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><b>PIPPING PHASE</b><br><span style="font-size:3rem; font-weight:bold;">{pip}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><b>NEURAL SYNC</b><br><span style="font-size:3rem; font-weight:bold;">100%</span></div>', unsafe_allow_html=True)

        st.subheader("🚨 Biological Guardrails")
        limit = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        # FIXED: Using bin.harvest_date as egg.created_at is missing from schema
        res = supabase.table("egg").select("egg_id, bin(mother(mother_name), harvest_date)").eq("current_stage", "Mature").execute().data
        
        alerts = 0
        if res:
            for egg in res:
                h_date = egg.get('bin', {}).get('harvest_date') if egg.get('bin') else None
                if h_date and h_date < limit:
                    m_name = egg['bin']['mother']['mother_name'] if egg['bin'].get('mother') else "Unknown"
                    st.warning(f"⚠️ OVERDUE: Egg {egg['egg_id']} ({m_name}) - Harvested: {h_date}")
                    alerts += 1
        if alerts == 0: st.success("✓ Biological markers stable.")

    except Exception as e: st.error(f"Database Error: {e}")

elif menu == "🐣 NEW INTAKE":
    st.markdown("<h1>New Intake</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("intake_v50", clear_on_submit=True):
        species_data = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in species_data}
        
        c1, c2 = st.columns(2)
        m_name = c1.text_input("Mother Name (Origin Identifier)", placeholder="Shelly")
        m_spec = c2.selectbox("Species Class", list(spec_map.keys()))
        qty = st.number_input("Egg Quantity", 1, 100, 10)
        
        # TITANIUM PRIMARY BUTTON
        if st.form_submit_button("SAVE INTAKE & REGISTER EGGS"):
            try:
                m_res = supabase.table("mother").select("mother_id").eq("mother_name", m_name).execute()
                m_id = m_res.data[0]['mother_id'] if m_res.data else supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec]}).execute().data[0]['mother_id']
                b_id = supabase.table("bin").insert({"mother_id": m_id, "total_eggs": qty, "harvest_date": datetime.now().strftime('%Y-%m-%d')}).execute().data[0]['bin_id']
                batch = [{"bin_id": b_id, "current_stage": "Incubating", "status": "Active"} for _ in range(int(qty))]
                supabase.table("egg").insert(batch).execute()
                st.balloons()
                st.success(f"Vault Updated: {qty} eggs saved for {m_name}.")
            except Exception as e: st.error(f"Intake Failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Vault Registry</h1>", unsafe_allow_html=True)
    df = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(df, use_container_width=True)

