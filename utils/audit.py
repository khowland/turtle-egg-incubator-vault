"""
=============================================================================
Module:     utils/audit.py
Project:    Incubator Vault v7.9.9 — Wildlife In Need Center (WINC)
Purpose:    system_log auditing wrapper for ensuring all write operations
            follow §35 Enterprise Naming Standards.
Author:     Antigravity (Sovereign Sprint Edition)
Modified:   2026-04-11 (Phase-C Implementation)
=============================================================================
"""

import streamlit as st
from utils.db import get_supabase_client, clear_vault_cache
from utils.logger import logger

# =============================================================================
# WRAPPER: logged_write()
# =============================================================================

def logged_write(supabase, session_id, event_type, payload_dict, db_operations_fn):
    """Execute a database function and log the result to system_log.
    
    Wrapped in try/except to ensure both successes and failures are
    audited. After a successful write, clears Streamlit's data cache
    to ensure the UI reflects the new database state immediately.
    """
    
    try:
        # 1. Execute the core biological transaction
        result = db_operations_fn()
        
        # 2. Log Success to system_log
        supabase.table("system_log").insert({
            "session_id": session_id,
            "event_type": event_type,
            "event_message": f"SUCCESS: {event_type} (Entries: {len(payload_dict) if isinstance(payload_dict, list) else 1})",
            "metadata": {"payload": payload_dict}
        }).execute()
        
        # 3. CRITICAL: Clear cache so the 'resilient ledger' reflects reality
        clear_vault_cache()
        
        return result

    except Exception as e:
        # 4. Log Failure to system_log for forensic triage
        err_msg = f"FAILURE: {event_type} - {str(e)}"
        logger.error(f"❌ Audit: {err_msg}")
        
        try:
            supabase.table("system_log").insert({
                "session_id": session_id,
                "event_type": "ERROR",
                "event_message": err_msg,
                "metadata": {"error_details": str(e), "failed_payload": payload_dict}
            }).execute()
        except Exception as log_err:
            # If even the error log fails, log to console — don't lose the original error
            logger.error(f"⚠️ Audit: Failed to log error to system_log: {log_err}")
        
        # Re-raise for UI-level error handling
        raise e

def safe_db_execute(operation_name, db_func, success_message=None):
    """Simple UI-level wrapper for audit logging without complex payloads."""
    from utils.db import get_supabase
    supabase = get_supabase()
    session_id = st.session_state.get('session_id', 'UNKNOWN')
    
    try:
        res = db_func()
        if success_message:
            supabase.table("system_log").insert({
                "session_id": session_id,
                "event_type": "ACCESS",
                "event_message": success_message
            }).execute()
        return res
    except Exception as e:
        st.error(f"❌ Biological Ledger Error ({operation_name}): {str(e)}")
        raise e
