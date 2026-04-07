"""
=============================================================================
Module:     utils/db.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Supabase client initialization and singleton management with
            Streamlit resource caching. Includes credential validation
            and cache management for auto-sync after writes.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Code Review: Restored credential validation,
            added enterprise comments)
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
    """Initializes and returns a cached Supabase client instance.
    
    Reads credentials from .env and creates a singleton-like client
    managed by Streamlit's cache_resource to prevent re-initialization.
    
    Returns:
        Client: An authenticated Supabase client.
        
    Raises:
        SystemExit: If SUPABASE_URL or SUPABASE_KEY are missing.
    """
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
    """Clears Streamlit's data cache to force fresh reads from Supabase.
    
    Called automatically after every successful write operation via
    the logged_write() audit wrapper. This ensures the UI always
    reflects the latest database state without manual refresh.
    """
    logger.warning("🧹 Autonomous Sync: Clearing data cache for fresh reads.")
    st.cache_data.clear()

# -----------------------------------------------------------------------------
# Function: check_connection
# Description: Pings Supabase to verify connectivity on startup or refresh.
# Returns: bool — True if connection is live
# -----------------------------------------------------------------------------
def check_connection(supabase: Client) -> bool:
    """Verifies connectivity to the Supabase backend.
    
    Attempts a simple select on the species table to ensure the link is live.
    Used by the Neural Refresh button and startup diagnostics.
    
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        supabase.table("species").select("species_id").limit(1).execute()
        logger.info("✅ Supabase connection verified.")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        return False

# Alias for easier imports
get_supabase = get_supabase_client
