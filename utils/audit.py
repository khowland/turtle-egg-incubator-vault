"""
=============================================================================
Module:     utils/audit.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    SystemLog auditing wrapper for ensuring all write operations
            are tracked with session metadata.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st

# =============================================================================
# SECTION: Audit Log Wrapper
# =============================================================================

def logged_write(supabase, session_id, event_type, payload_dict, db_operations_fn):
    """Execute a database function and log the result to SystemLog.
    
    Wrapped in a try-except block to ensure failures are also audited.
    
    Args:
        supabase: The active Supabase client.
        session_id: The current observer's session_id.
        event_type: String constant from Requirements §2.I.
        payload_dict: Dictionary containing the data changed or created.
        db_operations_fn: A lambda or function that performs the actual SQL.
        
    Returns:
        Any: The result of the db_operations_fn if successful.
        
    Raises:
        Exception: Re-raises any DB exception after logging the error.
    """
    try:
        # Execute the actual database work
        result = db_operations_fn()
        
        # Requirement: Log success to SystemLog
        supabase.table("SystemLog").insert({
            "session_id": session_id,
            "event_type": event_type,
            "event_message": f"{event_type} completed successfully",
            "payload": payload_dict
        }).execute()
        
        return result
        
    except Exception as e:
        # Requirement: Log all failures to SystemLog with ERROR type
        supabase.table("SystemLog").insert({
            "session_id": session_id,
            "event_type": "ERROR",
            "event_message": f"Failure during {event_type}: {str(e)}",
            "payload": payload_dict
        }).execute()
        
        # Re-raise for UI handling
        raise e
