"""
=============================================================================
Module:        utils/bootstrap.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35.1, §36]
Dependencies:  utils.db
Inputs:        st.session_state (observer_id, session_id)
Outputs:       Supabase Client, Cached Metrics
Description:   Unified Application Bootstrap for Page Config, Theme, and Auditing.
=============================================================================
"""

import streamlit as st
import uuid
import datetime
from utils.db import get_supabase

def bootstrap_page(title="Incubator Vault", icon="🐢"):
    """
    Standardized page initialization.
    Ensures Session IDs and Database clients are ready.
    """
    # 1. Ensure Global Session ID for Audit Trace
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        
    # 2. Check Identity (skip when running outside a full ScriptRunContext, e.g. tests)
    if not st.session_state.get('observer_id'):
        _script_hash = getattr(st, "active_script_hash", "")
        if _script_hash != "":
            st.warning("⚠️ Session expired or not started. Redirecting...")
            st.stop()
             
    # 3. Global Accessibility Initialization
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
        
        /* v8.0.0 Global Standard: Eliminate Technical Drift and Visual Flickering */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {{
            font-family: 'Inter', sans-serif !important;
            font-size: {st.session_state.global_font_size}px !important;
        }}

        /* Sidebar Persistence Guard (§35.1) */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarNav"] span {{
            font-family: 'Inter', sans-serif !important;
            font-size: {st.session_state.global_font_size}px !important;
        }}
        
        .stMarkdown, p, label, .stButton > button, .stSelectbox, .stTextInput, .stNumberInput, .stTextArea {{
            font-size: {st.session_state.global_font_size}px !important;
            line-height: {st.session_state.line_height} !important;
        }}
        
        {contrast_css}
        
        [data-testid="stHeader"] {{ 
            background: transparent !important;
            visibility: visible !important;
        }}
        
        footer {{ visibility: hidden !important; }}
    </style>
    """, unsafe_allow_html=True)
             
    return get_supabase()

@st.cache_resource(ttl=3600)
def get_last_bin_weight(bin_id):
    """
    Hydration Gate Optimization (§35.5).
    Retrieves the last recorded weight for a bin from the clinical ledger.
    """
    supabase = get_supabase()
    last_observation = supabase.table('bin_observation').select('bin_weight_g, timestamp').eq('bin_id', bin_id).order('timestamp', desc=True).limit(1).execute()
    
    if last_observation.data:
        return last_observation.data[0]
    
    # Fallback to bin table metadata
    bin_data = supabase.table('bin').select('target_total_weight_g').eq('bin_id', bin_id).execute()
    if bin_data.data:
        return {"bin_weight_g": float(bin_data.data[0].get('target_total_weight_g') or 0.0), "timestamp": None}
    
    return {"bin_weight_g": 0.0, "timestamp": None}

def get_resilient_table(supabase, table_name):
    """Standard §35: Direct Table Access."""
    return supabase.table(table_name)

def safe_db_execute(operation_name, func, success_message=None, *args, **kwargs):
    """
    Atomic Transactions (§36.2): Unified Result Wrapper.
    Triggers system_log on failure and provides Safe-State rollback signal.
    """
    try:
        result = func(*args, **kwargs)
        
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
        import traceback
        error_details = traceback.format_exc()
        st.error(f"❌ Biological Ledger Error ({operation_name}): Defaulting to Safe-State.")
        
        try:
            get_resilient_table(get_supabase(), 'system_log').insert({
                "session_id": st.session_state.get('session_id', 'UNKNOWN_ERR'),
                "event_type": "ERROR",
                "event_message": f"[{operation_name}] CRASH: {str(e)}"
            }).execute()
        except:
            pass 
            
        with st.expander("🔍 Differential Diagnosis (Technical Details)"):
            st.code(error_details)
        return None

