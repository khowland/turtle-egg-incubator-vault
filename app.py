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

# Force Wide Layout and high-contrast icon
st.set_page_config(
    page_title="Vault Elite 2026",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. TITANIUM CSS OVERRIDES (FIXES ALL VISIBILITY ISSUES) ---
# This CSS uses extreme specificity to force colors regardless of Streamlit's theme.
st.markdown("""
<style>
    /* 1. GLOBAL BACKGROUND & TEXT */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #020617 !important;
        color: #FFFFFF !important;
    }

    /* 2. SIDEBAR - FORCED WHITE TEXT (FIXES DARK-ON-DARK) */
    /* We target every possible text container inside the sidebar */
    [data-testid="stSidebar"], [data-testid="stSidebar"] * {
        background-color: #0F172A !important; 
        color: #FFFFFF !important;
    }
    /* Specifically target radio button labels and navigation links */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p, 
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    /* 3. BUTTON - FORCED EMERALD (FIXES WHITE-ON-WHITE) */
    /* Targeting the button and its nested paragraph tag */
    div.stButton > button {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        border: 2px solid #059669 !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        height: 70px !important;
        width: 100% !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4) !important;
    }
    div.stButton > button p {
        color: #FFFFFF !important;
        font-size: 1.2rem !important;
    }
    div.stButton > button:hover {
        background-color: #059669 !important;
        border-color: #FFFFFF !important;
    }

    /* 4. FORM FIELD LABELS */
    [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* 5. SELECTBOX/DROPDOWN FIX */
    /* Fix text inside the selected box and the dropdown menu */
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="popover"] {
        background-color: #1E293B !important;
    }
    div[data-baseweb="popover"] * {
        color: #FFFFFF !important;
    }

    /* Hide default UI clutter */
    #MainMenu, footer, header { visibility: hidden; }
    /* But show header for the toggle button if needed */
    [data-testid="stHeader"] { visibility: visible !important; background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE CLIENT ---
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
    st.markdown("<h1 style='color:white; font-size:3rem; margin-bottom:0;'>VAULT</h1><p style='color:#10B981; font-weight:bold; letter-spacing:3px;'>ELITE PRO</p>", unsafe_allow_html=True)
    anim_data = load_lottieurl("https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json")
    if anim_data: st_lottie(anim_data, height=140, key="nav_anim")
    
    menu = st.radio("SYSTEM ACCESS", ["📈 DASHBOARD", "🐣 NEW INTAKE", "🔍 FIELD LOG", "🛠️ REGISTRY"])

# --- 5. APPLICATION VIEWS ---
if menu == "📈 DASHBOARD":
    st.markdown("<h1>System Insights</h1>", unsafe_allow_html=True)
    try:
        # Metrics
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count or 0
        pip = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count or 0
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Active Eggs", active)
        with c2: st.metric("Pipping Now", pip)
        with c3: st.metric("System Sync", "100%")

        # ALERTS (Corrected Schema: Use bin.harvest_date as egg.created_at is missing)
        st.subheader("🚨 Biological Guardrails")
        limit_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
        late_eggs = supabase.table("egg").select("egg_id, bin(mother(mother_name), harvest_date)").eq("current_stage", "Mature").execute().data
        
        alerts = 0
        if late_eggs:
            for egg in late_eggs:
                h_date = egg['bin']['harvest_date'] if egg.get('bin') else None
                if h_date and h_date < limit_date:
                    m_name = egg['bin']['mother']['mother_name'] if egg['bin'].get('mother') else "Unk"
                    st.warning(f"⚠️ OVERDUE: Egg {egg['egg_id']} ({m_name}) - Harvested: {h_date}")
                    alerts += 1
        
        if alerts == 0: st.success("✓ All biological markers within safe zones.")

    except Exception as e: st.error(f"Neural Link Error: {e}")

elif menu == "🐣 NEW INTAKE":
    st.markdown("<h1>New Intake</h1>", unsafe_allow_html=True)
    
    with st.form("new_intake_form", clear_on_submit=True):
        species_list = [s['common_name'] for s in supabase.table("species").select("common_name").execute().data]
        spec_map = {s['common_name']: s['species_id'] for s in supabase.table("species").select("species_id, common_name").execute().data}
        
        c1, c2 = st.columns(2)
        mother_name = c1.text_input("Origin Identifier (Mother Name)", placeholder="e.g., Shelly")
        species_name = c2.selectbox("Biological Class (Species)", species_list)
        quantity = st.number_input("Egg Quantity", 1, 100, 10)
        
        # SUBMIT BUTTON (Fixed Visibility: Forced Emerald Green with White Text)
        if st.form_submit_button("SAVE INTAKE & REGISTER EGGS"):
            try:
                # 1. Mother logic
                m_res = supabase.table("mother").select("mother_id").eq("mother_name", mother_name).execute()
                m_id = m_res.data[0]['mother_id'] if m_res.data else \
                       supabase.table("mother").insert({"mother_name": mother_name, "species_id": spec_map[species_name]}).execute().data[0]['mother_id']
                
                # 2. Bin logic
                b_id = supabase.table("bin").insert({"mother_id": m_id, "total_eggs": quantity, "harvest_date": datetime.now().strftime('%Y-%m-%d')}).execute().data[0]['bin_id']
                
                # 3. Eggs logic
                eggs = [{"bin_id": b_id, "current_stage": "Incubating", "status": "Active"} for _ in range(int(quantity))]
                supabase.table("egg").insert(eggs).execute()
                
                st.balloons()
                st.success(f"Successfully saved {quantity} eggs for {mother_name}!")
            except Exception as e: st.error(f"Intake Failed: {e}")

elif menu == "🔍 FIELD LOG":
    st.markdown("<h1>Field Analysis</h1>", unsafe_allow_html=True)

elif menu == "🛠️ REGISTRY":
    st.markdown("<h1>Registry View</h1>", unsafe_allow_html=True)
    df = pd.DataFrame(supabase.table("species").select("*").execute().data)
    st.dataframe(df, use_container_width=True)

