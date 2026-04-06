"""
=============================================================================
Module:     utils/db.py
Purpose:    Supabase client singleton with global cache-clearing logic.
=============================================================================
"""
import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_supabase_client() -> Client:
    """Initialize and cache the Supabase client connection."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def clear_vault_cache():
    """Force clear all cached data to ensure UI sync with database."""
    st.cache_data.clear()
