"""
=============================================================================
Module:     utils/bootstrap.py (NEW - CAP.01)
Project:    Incubator Vault v7.2.0 — WINC
Purpose:    Unified Application Bootstrap for Page Config, Theme, and DB.
Revision:   2026-04-08 — Initial Release (Antigravity)
=============================================================================
"""

import streamlit as st
import uuid
from utils.db import get_supabase

def bootstrap_page(title="Incubator Vault", icon="🐢"):
    """
    Standardized page initialization.
    Ensures Session IDs and Database clients are ready.
    """
    st.set_page_config(page_title=f"{title} | WINC", page_icon=icon, layout="wide")
    
    # 1. Ensure Global Session ID for Audit Trace
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
        
    # 2. Check Identity
    if not st.session_state.get('observer_id'):
        if st.active_script_hash != "": # Prevent loop on splash
             st.warning("⚠️ Session expired or not started. Redirecting...")
             st.stop()
             
    # 3. Global Mobile Font Scaling
    if 'global_font_size' not in st.session_state:
        st.session_state.global_font_size = 18 # Default boosted to 18px for mobile readability
        
    st.markdown(f"""
    <style>
        /* Force upscale on all major Streamlit text components */
        p, div, label, span, .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
            font-size: {st.session_state.global_font_size}px !important;
        }}
        /* Hide confusing Streamlit Developer Toolbar menu */
        [data-testid="stHeader"] {{
            visibility: hidden;
        }}
    </style>
    """, unsafe_allow_html=True)
             
    return get_supabase()

def safe_db_execute(operation_name, func, *args, **kwargs):
    """
    CAP.02: Unified Result Wrapper for robust exception handling.
    """
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        st.error(f"❌ Biological Ledger Error ({operation_name}): Defaulting to Safe-State. Please contact Administrator.")
        
        # 🚨 TELEMETRY: Record error to SystemLog for debugging
        try:
            # We use Upsert on SessionLog just in case the app bypassed the login splash screen
            get_supabase().table('SessionLog').upsert({"session_id": st.session_state.get('session_id', 'UNKNOWN_ERR'), "user_name": "System"}).execute()
            
            get_supabase().table('systemlog').insert({
                "session_id": st.session_state.get('session_id', 'UNKNOWN_ERR'),
                "event_type": "ERROR",
                "event_message": f"[{operation_name}] CRASH: {str(e)}"
            }).execute()
        except:
            pass # Failsafe if DB itself is unresponsive
            
        return None
