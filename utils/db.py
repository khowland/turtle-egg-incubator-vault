"""
=============================================================================
Module:        utils/db.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  supabase, python-dotenv
Inputs:        Enviroment Variables (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
Outputs:       Supabase Client Singleton
Description:   Supabase client initialization and singleton management.
=============================================================================
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
from utils.logger import logger

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# SECTION: Supabase Client Factory
# Description: Singleton pattern via @st.cache_resource. Prevents re-creating
#              the client on every Streamlit page re-run.
# =============================================================================

@st.cache_resource
def get_supabase_client() -> Client:
    """Initializes and returns a cached Supabase client instance."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    # Requirement: Fail fast with clear error if credentials are missing
    if not url or not key:
        logger.error("❌ Supabase credentials missing from .env environment.")
        st.error("❌ **Supabase credentials missing.** Check your `.env` file for `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.")
        st.stop()
    
    logger.info(f"🔌 Initializing Supabase Connection: {url[:40]}...")
    return create_client(url, key)

# =============================================================================
# SECTION: Cache Management
# Description: Auto-sync helper that clears cached data after write operations.
#              Called by audit.py after every successful logged_write().
# =============================================================================

def clear_vault_cache():
    """Clears Streamlit's data cache to force fresh reads from Supabase."""
    logger.warning("🧹 Autonomous Sync: Clearing data cache for fresh reads.")
    st.cache_data.clear()

# -----------------------------------------------------------------------------
# Function: check_connection
# Description: Pings Supabase to verify connectivity on startup or refresh.
# Returns: bool — True if connection is live
# -----------------------------------------------------------------------------
def check_connection(supabase: Client) -> bool:
    """Verifies connectivity to the Supabase backend."""
    try:
        supabase.table("species").select("species_id").limit(1).execute()
        logger.info("✅ Supabase connection verified.")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

# Alias for easier imports
get_supabase = get_supabase_client
