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
    page_title="Incubator Vault v3.2",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. THEME & STYLING ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { border-radius: 10px; border: 1px solid #ddd; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. UTILS & DATA ---
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

def wake_up_supabase():
    headers = {"Authorization": f"Bearer {SUPABASE_MGMT_TOKEN}"}
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/unpause"
    try:
        requests.get(SUPABASE_URL, timeout=1)
    except:
        with st.status("🐢 Waking up the Vault...", expanded=True) as status:
            resp = requests.post(url, headers=headers)
            if resp.status_code in [200, 201, 409]:
                st.write("Spinning up database (30s)...")
                time.sleep(25)
                status.update(label="Vault is Awake!", state="complete", expanded=False)
                st.rerun()

# --- 4. SESSION & NAVIGATION ---
if 'session_id' not in st.session_state:
    user = "Elisa"
    sid = f"{user}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state.session_id = sid
    st.session_state.user_name = user
    try:
        supabase = get_supabase()
        supabase.table("sessionlog").insert({"session_id": sid, "user_name": user, "user_agent": "Field-App-v3.2"}).execute()
    except: pass

supabase = get_supabase()

# Sidebar
st.sidebar.title("🐢 Incubator Vault")
# Animation with crash-proof check
lottie_url = "https://lottie.host/880a6c0c-7b0f-48d5-94f4-500b41050682/L3zS0XvU7Y.json"
lottie_data = load_lottieurl(lottie_url)

with st.sidebar:
    if lottie_data:
        st_lottie(lottie_data, height=120, key="vault_anim")
    else:
        st.markdown("## 🐢") # Fallback emoji if animation fails
    
    st.caption(f"Observer: {st.session_state.user_name}")
    st.caption(f"ID: {st.session_state.session_id}")
    menu = st.radio("Menu", ["📊 Dashboard", "📥 Intake", "🔍 Observation", "🛠️ Tables"])

# --- 5. PAGES ---
if menu == "📊 Dashboard":
    st.title("Vault Dashboard")
    wake_up_supabase()
    
    try:
        active = supabase.table("egg").select("egg_id", count="exact").eq("status", "Active").execute().count
        pipping = supabase.table("egg").select("egg_id", count="exact").eq("current_stage", "Pipping").execute().count
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Eggs", active or 0)
        c2.metric("Pipping Watch", pipping or 0)
        c3.metric("Health Status", "Secure ✅")
        
        st.divider()
        st.subheader("🚨 Recent Health Alerts")
        alerts = supabase.table("eggobservation").select("egg_id, molding, leaking, timestamp").or_("molding.eq.true,leaking.eq.true").order("timestamp", desc=True).limit(5).execute()
        if alerts.data:
            st.table(alerts.data)
        else:
            st.success("No current critical alerts.")
    except: st.info("Initializing vault data...")

elif menu == "📥 Intake":
    st.title("Bulk Intake")
    with st.form("intake"):
        spec_list = supabase.table("species").select("species_id, common_name").execute().data
        spec_map = {s['common_name']: s['species_id'] for s in spec_list}
        
        m_name = st.text_input("Mother Name", placeholder="Shelly")
        m_spec = st.selectbox("Species", options=list(spec_map.keys()))
        e_count = st.number_input("Egg Count", 1, 100, 10)
        if st.form_submit_button("Initialize Batch"):
            try:
                mid = supabase.table("mother").insert({"mother_name": m_name, "species_id": spec_map[m_spec], "created_by_session": st.session_state.session_id}).execute().data[0]['mother_id']
                bid = supabase.table("bin").insert({"mother_id": mid, "total_eggs": e_count, "created_by_session": st.session_state.session_id}).execute().data[0]['bin_id']
                eggs = [{"bin_id": bid, "created_by_session": st.session_state.session_id} for _ in range(e_count)]
                supabase.table("egg").insert(eggs).execute()
                st.balloons()
                st.success(f"Vault Entry Created: {bid}")
            except Exception as e: st.error(f"Failed: {e}")

elif menu == "🔍 Observation":
    st.title("Rapid Observation")
    bins = [b['bin_id'] for b in supabase.table("bin").select("bin_id").execute().data]
    sel_bin = st.selectbox("Bin", bins, index=None)
    if sel_bin:
        egg_list = [e['egg_id'] for e in supabase.table("egg").select("egg_id").eq("bin_id", sel_bin).execute().data]
        sel_eggs = st.multiselect("Eggs", egg_list)
        if sel_eggs:
            with st.form("obs"):
                c1, c2 = st.columns(2)
                v = c1.checkbox("Vascularity")
                m = c2.checkbox("Molding")
                l = c1.checkbox("Leaking")
                ch = c2.slider("Chalking", 0, 2, 0)
                stg = st.selectbox("New Stage", ["Developing", "Established", "Mature", "Pipping", "Hatched"])
                if st.form_submit_button("Save"):
                    obs = [{"egg_id": eid, "vascularity": v, "molding": m, "leaking": l, "chalking": ch, "session_id": st.session_state.session_id} for eid in sel_eggs]
                    supabase.table("eggobservation").insert(obs).execute()
                    for eid in sel_eggs: supabase.table("egg").update({"current_stage": stg}).eq("egg_id", eid).execute()
                    st.toast("Synchronized!", icon="✅")

elif menu == "🛠️ Tables":
    st.title("Lookup Management")
    data = supabase.table("species").select("*").execute().data
    st.dataframe(pd.DataFrame(data))

st.sidebar.divider()
if st.sidebar.button("Export CSV"):
    try:
        df = pd.DataFrame(supabase.table("eggobservation").select("*").execute().data)
        st.sidebar.download_button("Download", df.to_csv(index=False), "export.csv")
    except: st.sidebar.error("Export failed.")
