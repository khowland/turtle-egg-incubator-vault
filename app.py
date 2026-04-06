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
    page_title="Incubator Vault v3.1",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern look
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    .st-emotion-cache-1835u1n {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SUPABASE CONNECTION & WAKE-UP ---
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def wake_up_supabase():
    headers = {"Authorization": f"Bearer {SUPABASE_MGMT_TOKEN}"}
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/unpause"
    
    try:
        requests.get(SUPABASE_URL, timeout=2)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        with st.status("🐢 Waking up the Incubator Vault...", expanded=True) as status:
            st.write("The project is currently dormant. Triggering unpause...")
            resp = requests.post(url, headers=headers)
            if resp.status_code in [201, 200, 409]:
                st.write("Waiting for database to spin up (30s)...")
                time.sleep(25)
                status.update(label="Vault is awake!", state="complete", expanded=False)
                st.toast("System Online 🚀", icon="🐢")
            else:
                status.update(label="Wake-up failed!", state="error")
                st.error(f"Details: {resp.text}")

# --- 3. SESSION & AUDIT ---
if 'session_id' not in st.session_state:
    user_name = "Elisa"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.session_id = f"{user_name}_{timestamp}"
    st.session_state.user_name = user_name
    
    supabase = get_supabase()
    try:
        supabase.table("sessionlog").insert({"session_id": st.session_state.session_id, "user_name": user_name, "user_agent": "Streamlit-Vault-v3.1"}).execute()
    except Exception:
        pass # Handle case where DB is paused later

supabase = get_supabase()

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🐢 Incubator Vault")
lottie_turtle = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_m6vsmq.json")
with st.sidebar:
    if lottie_turtle:
            st_lottie(lottie_turtle, height=150, key="sidebar_lottie")
    st.write(f"**Session:** `{st.session_state.session_id}`")
    st.write(f"**Observer:** {st.session_state.user_name}")

menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "📥 Intake Wizard", "🔍 Rapid Observation", "🛠️ Lookup Tables"])

# --- 5. PAGE: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("🚀 Vault Insights")
    wake_up_supabase()
    
    col1, col2, col3 = st.columns(3)
    try:
        active_eggs = supabase.table("egg").select("*", count="exact").eq("status", "Active").execute()
        pipping = supabase.table("egg").select("*", count="exact").eq("current_stage", "Pipping").execute()
        
        col1.metric("Active Eggs", active_eggs.count if active_eggs.count else 0, delta="Stable")
        col2.metric("Pipping Watch", pipping.count if pipping.count else 0, delta="Attention Needed", delta_color="inverse")
        col3.metric("System Health", "Optimal", delta="Verified")

        st.divider()
        st.subheader("⚠️ Critical Health Monitoring")
        alerts = supabase.table("eggobservation").select("egg_id, molding, leaking, timestamp").or_("molding.eq.true,leaking.eq.true").order("timestamp", desc=True).limit(5).execute()
        if alerts.data:
            df_alerts = pd.DataFrame(alerts.data)
            st.dataframe(df_alerts.style.highlight_max(axis=0, subset=['molding', 'leaking'], color='#ffcccc'), use_container_width=True)
        else:
            st.success("No current health warnings detected. All eggs stable.")
    except Exception:
        st.info("Waking up the vault... Data will appear shortly.")

# --- 6. PAGE: INTAKE WIZARD ---
elif menu == "📥 Intake Wizard":
    st.title("📥 Burst Intake Wizard")
    
    with st.container(border=True):
        with st.form("intake_form", border=False):
            st.subheader("1. Mother Identity")
            species_list = supabase.table("species").select("species_id, common_name").execute()
            species_options = {s['common_name']: s['species_id'] for s in species_list.data}
            
            c1, c2 = st.columns(2)
            m_name = c1.text_input("Mother Name", placeholder="e.g. Shelly")
            m_species = c2.selectbox("Species", options=list(species_options.keys()))
            m_date = st.date_input("Intake Date", value=datetime.now())
            
            st.divider()
            st.subheader("2. Bin & Egg Count")
            egg_count = st.number_input("Total Eggs Harvested", min_value=1, max_value=100, value=12)
            
            submitted = st.form_submit_button("✨ INITIALIZE VAULT ENTRY")
            
            if submitted:
                try:
                    mother_resp = supabase.table("mother").insert({"mother_name": m_name, "species_id": species_options[m_species], "intake_date": str(m_date), "created_by_session": st.session_state.session_id}).execute()
                    mother_id = mother_resp.data[0]['mother_id']
                    bin_resp = supabase.table("bin").insert({"mother_id": mother_id, "harvest_date": str(m_date), "total_eggs": egg_count, "created_by_session": st.session_state.session_id}).execute()
                    bin_id = bin_resp.data[0]['bin_id']
                    eggs_to_insert = [{"bin_id": bin_id, "created_by_session": st.session_state.session_id} for _ in range(egg_count)]
                    supabase.table("egg").insert(eggs_to_insert).execute()
                    st.balloons()
                    st.success(f"Batch intake complete! Mother: {mother_id} | Bin: {bin_id}")
                except Exception as e:
                    st.error(f"Error during intake: {e}")

# --- 7. PAGE: RAPID OBSERVATION ---
elif menu == "🔍 Rapid Observation":
    st.title("🔍 Rapid Field Observation")
    
    bins = supabase.table("bin").select("bin_id").execute()
    bin_id = st.selectbox("Select Active Bin", [b['bin_id'] for b in bins.data], index=None, placeholder="Choose a bin...")
    
    if bin_id:
        eggs = supabase.table("egg").select("egg_id").eq("bin_id", bin_id).execute()
        selected_eggs = st.multiselect("Select Targeted Eggs", [e['egg_id'] for e in eggs.data])
        
        if selected_eggs:
            with st.container(border=True):
                with st.form("obs_form", border=False):
                    c1, c2 = st.columns(2)
                    vasc = c1.toggle("Vascularity ❤️")
                    mold = c2.toggle("Molding 🍄")
                    leak = c1.toggle("Leaking 💧")
                    chalk = c2.select_slider("Chalking Level", options=[0, 1, 2])
                    stage = st.selectbox("New Development Stage", ["Intake", "Developing", "Established", "Mature", "Pipping", "Hatched"])
                    notes = st.text_area("Field Notes")
                    
                    if st.form_submit_button("💾 SAVE OBSERVATIONS"):
                        obs_data = [{"egg_id": eid, "vascularity": vasc, "molding": mold, "leaking": leak, "chalking": chalk, "notes": notes, "session_id": st.session_state.session_id} for eid in selected_eggs]
                        supabase.table("eggobservation").insert(obs_data).execute()
                        for eid in selected_eggs:
                            supabase.table("egg").update({"current_stage": stage, "updated_by_session": st.session_state.session_id}).eq("egg_id", eid).execute()
                        st.toast("Observations Synchronized!", icon="✅")

# --- 8. PAGE: LOOKUP TABLES (CRUD) ---
elif menu == "🛠️ Lookup Tables":
    st.title("🛠️ System Configurations")
    table_choice = st.selectbox("Configuration Table", ["species"])
    
    if table_choice == "species":
        species_data = supabase.table("species").select("*").execute()
        df = pd.DataFrame(species_data.data)
        st.dataframe(df, use_container_width=True)
        
        with st.expander("➕ Register New Species", expanded=False):
            with st.form("species_crud"):
                s_id = st.text_input("Internal ID")
                c_name = st.text_input("Common Name")
                sci_name = st.text_input("Scientific Name")
                c1, c2 = st.columns(2)
                min_d = c1.number_input("Min Incubation", value=60)
                max_d = c2.number_input("Max Incubation", value=80)
                low_t = c1.number_input("Low Temp (°F)", value=75.0)
                high_t = c2.number_input("High Temp (°F)", value=85.0)
                if st.form_submit_button("Save to Vault"):
                    supabase.table("species").upsert({"species_id": s_id, "common_name": c_name, "scientific_name": sci_name, "incubation_min_days": min_d, "incubation_max_days": max_d, "optimal_temp_low": low_t, "optimal_temp_high": high_t}).execute()
                    st.rerun()

# --- 9. GLOBAL FOOTER & EXPORT ---
st.divider()
if st.sidebar.button("📦 PREPARE GLOBAL EXPORT"):
    csv = pd.DataFrame(supabase.table("eggobservation").select("*").execute().data).to_csv(index=False)
    st.sidebar.download_button("📥 DOWNLOAD VAULT DATA (CSV)", data=csv, file_name=f"vault_export_{datetime.now().strftime('%Y%m%d')}.csv")
