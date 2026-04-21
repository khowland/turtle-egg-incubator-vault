"""
=============================================================================
Module:        utils/db.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Upstream:      utils/audit.py, utils/bootstrap.py, utils/session.py
Downstream:    supabase, python-dotenv
Use Cases:     [Pending - Describe practical usage here]
Inputs:        Enviroment Variables (SUPABASE_URL, SUPABASE_ANON_KEY)
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
    # 1. Try Environment Variables (Local dev or Railway)
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    # 2. Try Streamlit Secrets (Community Cloud)
    if not url and "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
    if not key and "SUPABASE_ANON_KEY" in st.secrets:
        key = st.secrets["SUPABASE_ANON_KEY"]

    # Requirement: Fail fast with clear error if credentials are missing
    if not url or not key:
        logger.error("❌ Supabase credentials missing from .env environment.")
        st.error(
            "❌ **Supabase credentials missing.** Check your `.env` file for `SUPABASE_URL` and `SUPABASE_ANON_KEY`."
        )
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
    """Verifies connectivity to the Supabase backend with Auto-Wake (Plan B)."""
    try:
        supabase.table("species").select("species_id").limit(1).execute()
        logger.info("✅ Supabase connection verified.")
        return True
    except Exception as e:
        error_msg = str(e)
        # Requirement: Detect Paused state (usually 503 or 404 in connection string)
        if "503" in error_msg or "404" in error_msg or "Service Unavailable" in error_msg:
            logger.warning("🐢 Project Hibernation Detected. Attempting Plan B Wake-up...")
            
            # Use Streamlit UI feedback if running in a browser context
            try:
                st.warning("🐢 **Project Hibernation Detected.** Waking up the Vault... Please wait 60 seconds.")
            except:
                pass
            
            from utils.supabase_mgmt import wake_supabase_project, wait_for_restoration
            if wake_supabase_project():
                # Internal helper for quiet checks during polling
                def _check_quiet():
                    try:
                        supabase.table("species").select("species_id").limit(1).execute()
                        return True
                    except:
                        return False
                
                return wait_for_restoration(_check_quiet)
                
        logger.error(f"❌ Supabase connection failed: {e}")
        return False


# Alias for easier imports
get_supabase = get_supabase_client
