import streamlit as st
from utils.db import clear_vault_cache
from utils.logger import logger

def logged_write(supabase, session_id, action_type, metadata, write_func):
    logger.info(f"💾 Audit: Attempting {action_type} (Session: {session_id})")
    try:
        result = write_func()
        supabase.table("SystemLog").insert({
            "session_id": session_id, "action_type": action_type, "metadata": metadata
        }).execute()
        logger.info(f"✅ Audit: {action_type} successful. Payload: {metadata}")
        clear_vault_cache()
        return result
    except Exception as e:
        logger.error(f"❌ Audit: {action_type} FAILED: {str(e)}")
        supabase.table("SystemLog").insert({
            "session_id": session_id, "action_type": f"{action_type}_FAILED",
            "metadata": {"error": str(e), "original": metadata}
        }).execute()
        raise e
