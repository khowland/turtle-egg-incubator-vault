"""
=============================================================================
# Module:     utils/bootstrap.py (v7.9.4)
# Project:    Incubator Vault v7.9.4 — WINC
# Purpose:    Unified Application Bootstrap for Page Config, Theme, and Auditing.
# Revision:   2026-04-10 — Clinical Sovereignty Edition
# =============================================================================
"""

import streamlit as st
import uuid
from utils.db import get_supabase

def bootstrap_page(title="Incubator Vault", icon="🐢"):
    """
    Standardized page initialization.
    Ensures Session IDs and Database clients are ready.
    """
    # st.set_page_config removed v7.9.5 — now handled by app.py / st.navigation
    
    # 1. Ensure Global Session ID for Audit Trace
    if 'session_id' not in st.session_state:
        # Replaces truncated UUID with full UUID for audit integrity §6.59
        st.session_state.session_id = str(uuid.uuid4())
        
    # 2. Check Identity
    if not st.session_state.get('observer_id'):
        if st.active_script_hash != "": # Prevent loop on splash
             st.warning("⚠️ Session expired or not started. Redirecting...")
             st.stop()
             
    # 3. Global Accessibility Initialization v7.8.2
    if 'global_font_size' not in st.session_state: st.session_state.global_font_size = 18
    if 'line_height' not in st.session_state: st.session_state.line_height = 1.6
    if 'high_contrast' not in st.session_state: st.session_state.high_contrast = False
        
    contrast_css = ""
    if st.session_state.high_contrast:
        contrast_css = """
            body, .stApp { color: #000000 !important; background-color: #FFFFFF !important; }
            [data-testid="stHeader"] { background-color: #FFFFFF !important; }
            .stButton > button { border: 2px solid #000000 !important; font-weight: 800 !important; }
        """

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        /* Unified font through entire vault */
        html, body, [data-testid="stAppViewContainer"] {{
            font-family: 'Inter', sans-serif !important;
        }}
        
        /* Clinical Scoped font-size (§6.2) */
        .stMarkdown, p, label, .stButton > button, .stSelectbox, .stTextInput, .stNumberInput {{
            font-size: {st.session_state.global_font_size}px !important;
            line-height: {st.session_state.line_height} !important;
        }}
        
        {contrast_css}
        
        /* Ensure the toggle button is visible without intrusive styling */
        [data-testid="stHeader"] {{ 
            background: transparent !important;
            visibility: visible !important;
        }}
        
        footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)
             
    return get_supabase()

def get_resilient_table(supabase, table_name):
    """
    Standard §35: Direct Table Access.
    The database is fully transformed to singular snake_case.
    """
    return supabase.table(table_name)

def safe_db_execute(operation_name, func, success_message=None, *args, **kwargs):
    """
    CAP.02: Unified Result Wrapper for robust exception handling and auditing.
    """
    try:
        result = func(*args, **kwargs)
        
        # v7.9.3: Forensic Success Audit
        if success_message:
            try:
                get_resilient_table(get_supabase(), 'system_log').insert({
                    "session_id": st.session_state.get('session_id', 'SYSTEM'),
                    "event_type": "AUDIT",
                    "event_message": success_message
                }).execute()
            except: pass
            
        return result
    except Exception as e:
        st.error(f"❌ Biological Ledger Error ({operation_name}): Defaulting to Safe-State.")
        
        # 🚨 TELEMETRY: Record error to system_log for debugging
        try:
            get_resilient_table(get_supabase(), 'system_log').insert({
                "session_id": st.session_state.get('session_id', 'UNKNOWN_ERR'),
                "event_type": "ERROR",
                "event_message": f"[{operation_name}] CRASH: {str(e)}"
            }).execute()
        except:
            pass 
            
        return None
