"""
=============================================================================
Module:     utils/audit.py
Purpose:    Higher-order wrapper for atomic database writes and audit logging.
            Now includes automated cache clearing on success.
=============================================================================
"""
import streamlit as st
from utils.db import clear_vault_cache

def logged_write(supabase, session_id, action_type, metadata, write_func):
    """Execute a database write and log the action to SystemLog.
    
    Automatically clears the application cache if the write is successful.
    """
    try:
        # 1. Execute the actual database operation
        result = write_func()
        
        # 2. Log to SystemLog
        supabase.table("SystemLog").insert({
            "session_id": session_id,
            "action_type": action_type,
            "metadata": metadata
        }).execute()
        
        # 3. SELF-HEALING: Clear cache so user sees updates immediately
        clear_vault_cache()
        
        return result
    except Exception as e:
        # Log failure to system log too
        supabase.table("SystemLog").insert({
            "session_id": session_id,
            "action_type": f"{action_type}_FAILED",
            "metadata": {"error": str(e), "original": metadata}
        }).execute()
        raise e
