import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

@st.cache_resource
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    logger.info(f"🔌 Initializing Supabase Connection: {url}")
    return create_client(url, key)

def clear_vault_cache():
    logger.warning("🧹 Autonomous Sync: Clearing global data cache.")
    st.cache_data.clear()
