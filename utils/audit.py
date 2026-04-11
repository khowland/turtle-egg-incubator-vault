"""
=============================================================================
Module:     utils/audit.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    SystemLog auditing wrapper for ensuring all write operations
            are tracked with session metadata. Implements Requirements §7.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Code Review: Fixed column names to match schema,
            restored docstrings, added auto-cache clear)
=============================================================================
"""

import streamlit as st
from utils.db import get_supabase_client, clear_vault_cache
from utils.logger import logger

# =============================================================================
# SECTION: Audit Log Wrapper
# Description: Every database write in the application MUST go through this
#              function. It provides try/except logging to SystemLog and
#              auto-clears cached data so the UI reflects the latest state.
# =============================================================================

def logged_write(supabase, session_id, event_type, payload_dict, db_operations_fn):
    """Execute a database function and log the result to system_log.
    
    Wrapped in try/except to ensure both successes and failures are
    audited. After a successful write, clears Streamlit's data cache
    so subsequent page renders show fresh data.
    
    Args:
        supabase: The active Supabase client.
        session_id: The current observer's session_id (e.g. "elisa_20260406143000").
        event_type: String constant per Requirements §2.I (e.g. "INTAKE_COMPLETE").
        payload_dict: Dictionary containing the data changed or created.
        db_operations_fn: A callable that performs the actual SQL operations.
        
    Returns:
        Any: The result of db_operations_fn if successful.
        
    Raises:
        Exception: Re-raises any DB exception after logging the error.
    """
    logger.info(f"💾 Audit: Attempting {event_type} (Session: {session_id})")
    try:
        # Execute the actual database work
        result = db_operations_fn()
        
        # Requirement §35: Log success to system_log
        # Column names MUST match schema: event_type, event_message, payload (JSONB)
        supabase.table("system_log").insert({
            "session_id": session_id,
            "event_type": event_type,
            "event_message": f"{event_type} completed successfully",
            "payload": payload_dict
        }).execute()
        
        logger.info(f"✅ Audit: {event_type} successful. Payload: {payload_dict}")
        
        # Auto-clear cached data so the UI refreshes with new data
        clear_vault_cache()
        
        return result
        
    except Exception as e:
        # Requirement §35: Log all failures to system_log with ERROR type
        logger.error(f"❌ Audit: {event_type} FAILED: {str(e)}")
        try:
            supabase.table("system_log").insert({
                "session_id": session_id,
                "event_type": "ERROR",
                "event_message": f"Failure during {event_type}: {str(e)}",
                "payload": payload_dict
            }).execute()
        except Exception as log_err:
            # If even the error log fails, log to console — don't lose the original error
            logger.error(f"⚠️ Audit: Failed to log error to system_log: {log_err}")
        
        # Re-raise for UI-level error handling
        raise e
