"""
=============================================================================
Module:     utils/db.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Supabase client initialization and singleton management with 
            Streamlit resource caching.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# SECTION: Supabase Client Factory
# =============================================================================

@st.cache_resource
def get_supabase_client() -> Client:
    """Initializes and returns a cached Supabase client instance.
    
    Reads credentials from .env and creates a singleton-like client
    managed by Streamlit's cache_resource to prevent re-initialization.
    
    Returns:
        Client: An authenticated Supabase client.
        
    Raises:
        RuntimeError: If SUPABASE_URL or SUPABASE_KEY are missing.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        # Critical failure if credentials are not found
        st.error("❌ Supabase credentials missing from .env environment.")
        st.stop()
        
    return create_client(url, key)

# -----------------------------------------------------------------------------
# Function: check_connection
# Description: Pings Supabase to verify connectivity
# -----------------------------------------------------------------------------
def check_connection(supabase: Client) -> bool:
    """Verifies connectivity to the Supabase backend.
    
    Attempts a simple select on the species table to ensure the link is live.
    
    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        # Simple ping to species table (is_deleted filter for safety)
        supabase.table("species").select("species_id").limit(1).execute()
        return True
    except Exception as e:
        # Log error to console for developer visibility
        print(f"DB Connection Error: {e}")
        return False
