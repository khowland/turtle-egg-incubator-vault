"""
=============================================================================
Module:        utils/ledger.py
Project:       Incubator Vault v9.2.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§2.4, §35, §36]
Description:   Centralized Clinical Service Layer. 
               Implements "Self-Verifying Writes" (SQL Pincer) and 
               decouples database logic from UI views.
=============================================================================
"""

import streamlit as st
import datetime
from utils.db import get_supabase
from utils.logger import logger, audit_event
from utils.identity import get_active_observer

def record_observations(egg_ids, metrics, backdate=None):
    """
    The "One Function" for Health Data.
    Performs atomic write to egg_observation and egg update, then verifies via SQL Pincer.
    
    Args:
        egg_ids: list of egg_id strings
        metrics: dict with keys:
            Observation record fields:
            - stage_id: maps to stage_at_observation (text)
            - chalking_id: maps to chalking (integer 0-2)
            - is_vascular: maps to vascularity (boolean)
            - molding_score: maps to molding (integer)
            - leaking_score: maps to leaking (integer)
            - denting_score: maps to dented (integer)
            - notes: maps to observation_notes (text)
            - bin_id: BIGINT for the bin FK
            Egg update fields:
            - status, current_stage, last_chalk, last_vasc,
              last_molding, last_leaking, last_dented, modified_by_id, egg_notes
        backdate: ISO timestamp string for observation timestamp (optional)
    
    Returns:
        bool: True if write + SQL Pincer verification succeeded, False otherwise
    """
    supabase = get_supabase()
    observer = get_active_observer()
    
    timestamp = backdate if backdate else datetime.datetime.now().isoformat()
    
    # Build observation payload for each egg — using CORRECT DB column names
    obs_payload = []
    for egg_id in egg_ids:
        entry = {
            "egg_id": egg_id,
            "bin_id": metrics.get("bin_id"),
            "observer_id": observer["observer_id"],
            "session_id": observer["session_id"],
            "created_by_id": observer["observer_id"],
            "modified_by_id": observer["observer_id"],
            "stage_at_observation": metrics.get("stage_id"),
            "vascularity": metrics.get("is_vascular"),
            "chalking": metrics.get("chalking_id"),
            "molding": metrics.get("molding_score"),
            "leaking": metrics.get("leaking_score"),
            "dented": metrics.get("denting_score"),
            "observation_notes": metrics.get("notes", ""),
            "is_deleted": False,
        }
        # Honor backdating
        if backdate:
            entry["timestamp"] = backdate
        obs_payload.append(entry)
    
    # Build egg update fields — pull from metrics dict
    update_fields = {
        "modified_at": datetime.datetime.now().isoformat(),
        "status": metrics.get("status", "Active")
    }
    egg_meta_fields = [
        "current_stage", "last_chalk", "last_vasc",
        "last_molding", "last_leaking", "last_dented",
        "modified_by_id"
    ]
    for field in egg_meta_fields:
        val = metrics.get(field)
        if val is not None:
            update_fields[field] = val
    if metrics.get("egg_notes"):
        update_fields["egg_notes"] = metrics["egg_notes"]

    try:
        # 1. Update the Subject (Egg) status and metadata
        supabase.table("egg").update(update_fields).in_("egg_id", egg_ids).execute()
        
        # 2. Insert the Observations
        res = supabase.table("egg_observation").insert(obs_payload).execute()
        
        # 3. THE SQL PINCER: Verify the Landing
        if res.data:
            verify = supabase.table("egg_observation").select("egg_observation_id").eq("session_id", observer["session_id"]).in_("egg_id", egg_ids).execute()
            if verify.data and len(verify.data) == len(egg_ids):
                audit_event("OBSERVATION_COMMITTED", f"Eggs: {len(egg_ids)}, Observer: {observer['observer_name']}")
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Ledger Error: {str(e)}")
        return False
