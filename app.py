import streamlit as st
import os
import pandas as pd
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# --- 1. INITIALIZATION & SECRETS ---
load_dotenv('/workspace/.env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = "kxfkfeuhkdopgmkpdimo" 

st.set_page_config(
    page_title="Incubator Vault v3.0",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SUPABASE CONNECTION & WAKE-UP ---
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def wake_up_supabase():
    """Check if DB is responsive; if not, trigger Management API unpause."""
    headers = {"Authorization": f"Bearer {SUPABASE_MGMT_TOKEN}"}
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/unpause"
    
    try:
        requests.get(SUPABASE_URL, timeout=2)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        with st.spinner("🐢 Waking up the Incubator Vault... Please wait 30-60s."):
            resp = requests.post(url, headers=headers)
            if resp.status_code in [201, 200, 409]:
                time.sleep(20)
                st.success("Vault is awake!")
            else:
                st.error(f"Failed to wake up DB: {resp.text}")

# --- 3. SESSION & AUDIT ---
if 'session_id' not in st.session_state:
    user_name = "Elisa"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.session_id = f"{user_name}_{timestamp}"
    st.session_state.user_name = user_name

supabase = get_supabase()

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.title("🐢 Incubator Vault")
st.sidebar.write(f"**Session:** `{st.session_state.session_id}`")
st.sidebar.write(f"**Observer:** {st.session_state.user_name}")

menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "📥 Intake Wizard", "🔍 Rapid Observation", "🛠️ Lookup Tables"])

# --- 5. PAGE: DASHBOARD ---
if menu == "📊 Dashboard":
    st.header("Vault Dashboard")
    wake_up_supabase()
    
    col1, col2, col3 = st.columns(3)
    try:
        active_eggs = supabase.table("egg").select("*", count="exact").eq("status", "Active").execute()
        pipping = supabase.table("egg").select("*", count="exact").eq("current_stage", "Pipping").execute()
        
        col1.metric("Active Eggs", active_eggs.count if active_eggs.count else 0)
        col2.metric("Pipping Watch", pipping.count if pipping.count else 0)
        col3.metric("System Health", "Optimal ✅")

        st.subheader("⚠️ Critical Alerts (Molding / Leaking)")
        alerts = supabase.table("eggobservation").select("egg_id, molding, leaking, timestamp").or_("molding.eq.true,leaking.eq.true").order("timestamp", desc=True).limit(10).execute()
        if alerts.data:
            st.table(alerts.data)
        else:
            st.info("No critical health alerts at this time.")
    except Exception as e:
        st.warning(f"Could not load stats. DB might be waking up. Error: {e}")

# --- 6. PAGE: INTAKE WIZARD ---
elif menu == "📥 Intake Wizard":
    st.header("Burst Intake Wizard")
    
    with st.form("intake_form"):
        st.subheader("1. Mother Details")
        species_list = supabase.table("species").select("species_id, common_name").execute()
        species_options = {s['common_name']: s['species_id'] for s in species_list.data}
        
        m_name = st.text_input("Mother Name", placeholder="e.g. Shelly")
        m_species = st.selectbox("Species", options=list(species_options.keys()))
        m_date = st.date_input("Intake Date", value=datetime.now())
        
        st.subheader("2. Bin & Eggs")
        egg_count = st.number_input("Number of Eggs", min_value=1, max_value=100, value=10)
        
        submitted = st.form_submit_button("✨ Generate Batch")
        
        if submitted:
            try:
                mother_resp = supabase.table("mother").insert({
                    "mother_name": m_name,
                    "species_id": species_options[m_species],
                    "intake_date": str(m_date),
                    "created_by_session": st.session_state.session_id
                }).execute()
                mother_id = mother_resp.data[0]['mother_id']
                
                bin_resp = supabase.table("bin").insert({
                    "mother_id": mother_id,
                    "harvest_date": str(m_date),
                    "total_eggs": egg_count,
                    "created_by_session": st.session_state.session_id
                }).execute()
                bin_id = bin_resp.data[0]['bin_id']
                
                eggs_to_insert = [{"bin_id": bin_id, "created_by_session": st.session_state.session_id} for _ in range(egg_count)]
                supabase.table("egg").insert(eggs_to_insert).execute()
                st.success(f"Initialized Mother {mother_id}, Bin {bin_id}, and {egg_count} eggs!")
            except Exception as e:
                st.error(f"Intake failed: {e}")

# --- 7. PAGE: RAPID OBSERVATION ---
elif menu == "🔍 Rapid Observation":
    st.header("Rapid Observation UI")
    
    bins = supabase.table("bin").select("bin_id").execute()
    bin_id = st.selectbox("Select Bin", [b['bin_id'] for b in bins.data])
    
    if bin_id:
        eggs = supabase.table("egg").select("egg_id").eq("bin_id", bin_id).execute()
        selected_eggs = st.multiselect("Select Eggs to Observe", [e['egg_id'] for e in eggs.data])
        
        if selected_eggs:
            with st.form("obs_form"):
                col1, col2 = st.columns(2)
                vasc = col1.toggle("Vascularity")
                mold = col2.toggle("Molding")
                leak = col1.toggle("Leaking")
                chalk = col2.select_slider("Chalking", options=[0, 1, 2])
                stage = st.selectbox("Stage", ["Intake", "Developing", "Established", "Mature", "Pipping", "Hatched"])
                notes = st.text_area("Notes")
                
                save_obs = st.form_submit_button("💾 Save Observations")
                if save_obs:
                    obs_data = [{"egg_id": eid, "vascularity": vasc, "molding": mold, "leaking": leak, "chalking": chalk, "notes": notes, "session_id": st.session_state.session_id} for eid in selected_eggs]
                    supabase.table("eggobservation").insert(obs_data).execute()
                    for eid in selected_eggs:
                        supabase.table("egg").update({"current_stage": stage, "updated_by_session": st.session_state.session_id}).eq("egg_id", eid).execute()
                    st.success(f"Saved for {len(selected_eggs)} eggs.")

# --- 8. PAGE: LOOKUP TABLES (CRUD) ---
elif menu == "🛠️ Lookup Tables":
    st.header("Lookup Table Management")
    table_choice = st.selectbox("Select Table", ["species"])
    
    if table_choice == "species":
        st.subheader("Species Constants")
        species_data = supabase.table("species").select("*").execute()
        df = pd.DataFrame(species_data.data)
        st.dataframe(df, use_container_width=True)
        
        with st.expander("➕ Add / Edit Species"):
            with st.form("species_crud"):
                s_id = st.text_input("Species ID")
                c_name = st.text_input("Common Name")
                sci_name = st.text_input("Scientific Name")
                min_d = st.number_input("Min Days", value=60)
                max_d = st.number_input("Max Days", value=80)
                low_t = st.number_input("Low Temp", value=75.0)
                high_t = st.number_input("High Temp", value=85.0)
                status = st.text_input("Status", value="Common")
                if st.form_submit_button("Save"):
                    supabase.table("species").upsert({"species_id": s_id, "common_name": c_name, "scientific_name": sci_name, "incubation_min_days": min_d, "incubation_max_days": max_d, "optimal_temp_low": low_t, "optimal_temp_high": high_t, "vulnerability_status": status}).execute()
                    st.rerun()

# --- 9. GLOBAL FOOTER & EXPORT ---
st.divider()
if st.sidebar.button("Prepare CSV Export"):
    csv = pd.DataFrame(supabase.table("eggobservation").select("*").execute().data).to_csv(index=False)
    st.sidebar.download_button("📥 Download CSV", data=csv, file_name=f"vault_export_{datetime.now().strftime('%Y%m%d')}.csv")
