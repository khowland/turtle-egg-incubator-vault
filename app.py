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
VERSION = "v4.9 - NUCLEAR"

st.set_page_config(
    page_title=f"Vault Elite {VERSION}",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. NUCLEAR CSS OVERRIDES (ELITE v4.9) ---
# Specificity is key to overriding Streamlit's Emotion engine.
st.markdown("""
<style>
    /* 1. GLOBAL BACKGROUND & TEXT */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #020617 !important;
        color: #FFFFFF !important;
    }

    /* 2. SIDEBAR - FORCED HIGH CONTRAST (FIXES DARK-ON-DARK) */
    [data-testid="stSidebar"] {
        background-color: #050810 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    /* Force ALL text in sidebar to be pure white */
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Target navigation radio labels specifically */
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
    /* Set solid background and solid text color with zero transparency */
    div.stButton > button {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        border: 2px solid #34D399 !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        height: 75px !important;
        width: 100% !important;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3) !important;
    }
    /* Force the text INSIDE the button (Streamlit wraps it in a p tag) */
    div.stButton > button p, div.stButton > button * {
        color: #FFFFFF !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
    }
    div.stButton > button:hover {
        background-color: #059669 !important;
        transform: translateY(-4px);
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
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* Hide default header/footer but keep toggle button */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE ACCESS ---
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
    st.markdown("<h1 style='color:white; font-size:3.5rem; margin-bottom:0;'>VAULT</h1><p style='color:#10B981; font-weight:bold; letter-spacing:4px; margin-top:-10px;'>ELITE PRO</p>", unsafe_allow_html=True)
    anim_data = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim_data: st_lottie(anim_data, height=130, key="nav_anim")
    
    menu = st.radio("SYSTEM ACCESS", ["📊 DASHBOARD", "🐣 NEW INTAKE", "🔍 FIELD LOG", "🛠️ REGISTRY"])
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#10B981; font-weight:bold;'>CORE VERSION: {VERSION}</div>", unsafe_allow_html=True)

# --- 5. APPLICATION VIEWS ---
if menu == "📊 DASHBOARD":
    st.markdown("<h1>System Insights</h1>", unsafe_allow_html=True)
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="glass-card"><b>ACTIVE EGGS</b><br><span style="font-size:3rem; font-weight:bold;">{active}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="glass-card"><b>PIPPING PHASE</b><br><span style="font-size:3rem; font-weight:bold;">{pip}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="glass-card"><b>NEURAL SYNC</b><br><span style="font-size:3rem; font-weight:bold;">100%</span></div>', unsafe_allow_html=True)

        # ALERTS: Using bin.harvest_date (correcting missing created_at schema error)
        st.subheader("🚨 Biological Guardrails")
        limit = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        res = supabase.table("egg").select("egg_id, bin(mother(mother_name), harvest_date)").eq("current_stage", "Mature").execute().data
        
        alert_count = 0
        if res:
            for egg in res:
                h_date = egg['bin']['harvest_date'] if egg.get('bin') else None
                if h_date and h_date < limit:
                    m_name = egg['bin']['mother']['mother_name'] if egg['bin'].get('mother') else "Unknown"
                    st.warning(f"⚠️ OVERDUE: Egg {egg['egg_id']} ({m_name}) - Harvest Date: {h_date}")
                    alert_count += 1
        
        if alert_count == 0: st.success("✓ All biological markers stable.")

    except Exception as e: st.error(f"Database Error: {e}")

elif menu == "🐣 NEW INTAKE":
    st.markdown("<h1>New Intake</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    with st.form("intake_form_v49", clear_on_submit=True):
        species_data = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in species_data}
        
        c1, c2 = st.columns(2)
        mother_name = c1.text_input("Origin Identifier (Mother Name)", placeholder="Shelly")
        species_name = c2.selectbox("Biological Class (Species)", list(spec_map.keys()))
        quantity = st.number_input("Egg Quantity", 1, 100, 10)
        
        # FORCED HIGH-CONTRAST PRIMARY BUTTON
        if st.form_submit_button("SAVE INTAKE & REGISTER EGGS"):
            try:
                m_res = supabase.table("mother").select("mother_id").eq("mother_name", mother_name).execute()
                m_id = m_res.data[0]['mother_id'] if m_res.data else \
                       supabase.table("mother").insert(
                           {"mother_name": mother_name, "species_id": spec_map[species_name], "created_by_session": st.session_state.session_id}
                       ).execute().data[0]['mother_id']
                
                b_id = supabase.table("bin").insert(
                    {"mother_id": m_id, "total_eggs": quantity, "harvest_date": datetime.now().strftime('%Y-%m-%d'), "created_by_session": st.session_state.session_id}
                ).execute().data[0]['bin_id']
                
                batch = [{"bin_id": b_id, "current_stage": "Incubating", "status": "Active", "created_by_session": st.session_state.session_id} for _ in range(int(quantity))]
                supabase.table("egg").insert(batch).execute()
                
                st.balloons()
                st.success(f"Vault Updated: {quantity} eggs saved for {mother_name}.")
            except Exception as e: st.error(f"Intake Failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Registry View</h1>", unsafe_allow_html=True)
    df = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(df, use_container_width=True)

