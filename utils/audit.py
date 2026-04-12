"""
=============================================================================
Module:        utils/audit.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Upstream:      None (Entry point or dynamic)
Downstream:    utils.db, utils.logger
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (session_id)
Outputs:       system_log
Description:   System Log Auditing Wrapper for enterprise transaction standards.
=============================================================================
"""

import streamlit as st
from utils.db import get_supabase
from utils.logger import logger


def logged_write(
    supabase_client, session_id, event_type, payload_dictionary, db_operations_function
):
    """
    Execute a database function and log the result to system_log.
    Ensures both successes and failures are audited.
    """
    try:
        execution_result = db_operations_function()

        supabase_client.table("system_log").insert(
            {
                "session_id": session_id,
                "event_type": event_type,
                "event_message": f"SUCCESS: {event_type} (Entries: {len(payload_dictionary) if isinstance(payload_dictionary, list) else 1})",
                "metadata": {"payload": payload_dictionary},
            }
        ).execute()

        return execution_result

    except Exception as error:
        error_message = f"FAILURE: {event_type} - {str(error)}"
        logger.error(f"❌ Audit: {error_message}")

        try:
            supabase_client.table("system_log").insert(
                {
                    "session_id": session_id,
                    "event_type": "ERROR",
                    "event_message": error_message,
                    "metadata": {
                        "error_details": str(error),
                        "failed_payload": payload_dictionary,
                    },
                }
            ).execute()
        except Exception as log_error:
            logger.error(f"⚠️ Audit: Failed to log error to system_log: {log_error}")

        raise error


def safe_db_execute(operation_name, database_function, success_message=None):
    """Unified UI-level wrapper for audit logging."""
    supabase_client = get_supabase()
    current_session_id = st.session_state.get("session_id", "UNKNOWN")

    try:
        result = database_function()
        if success_message:
            supabase_client.table("system_log").insert(
                {
                    "session_id": current_session_id,
                    "event_type": "ACCESS",
                    "event_message": success_message,
                }
            ).execute()
        return result
    except Exception as error:
        st.error(f"❌ Biological Ledger Error ({operation_name}): {str(error)}")
        raise error
