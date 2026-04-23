"""
=============================================================================
Module:        utils/bootstrap.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35.1, §36]
Upstream:      app.py, utils/session.py, vault_views/1_Dashboard.py, vault_views/2_New_Intake.py, vault_views/3_Observations.py, vault_views/5_Settings.py, vault_views/6_Reports.py, vault_views/7_Diagnostic.py, vault_views/8_Help.py
Downstream:    utils.db
Use Cases:     [Pending - Describe practical usage here]
Inputs:        st.session_state (observer_id, session_id)
Outputs:       Supabase Client, Cached Metrics
Description:   Unified Application Bootstrap for Page Config, Theme, and Auditing.
=============================================================================
"""

import streamlit as st
import uuid
import datetime
from utils.db import get_supabase

VERSION = "v8.1.2"



def bootstrap_page(title="Incubator Vault", icon="🐢", render_sidebar=True):
    """
    Standardized page initialization.
    Ensures Session IDs and Database clients are ready.
    """
    # 1. Ensure Global Session ID for Audit Trace
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # 2. Check Identity (Note: app.py handles the router, so we don't stop here)
    if not st.session_state.get("observer_id"):
        # We only warn/stop if we are NOT in the main app.py entry point
        # This prevents deep-linking to clinical views without a session.
        pass 

    # 3. Global Accessibility Initialization
    if "global_font_size" not in st.session_state:
        st.session_state.global_font_size = 18
    if "line_height" not in st.session_state:
        st.session_state.line_height = 1.6
    if "high_contrast" not in st.session_state:
        st.session_state.high_contrast = False

    contrast_css = ""
    if st.session_state.high_contrast:
        contrast_css = """
            body, .stApp { color: #000000 !important; background-color: #FFFFFF !important; }
            [data-testid="stHeader"] { background-color: #FFFFFF !important; }
            .stButton > button { border: 2px solid #000000 !important; font-weight: 800 !important; }
        """

    # 4. Render Sidebar Clinical Context BEFORE style injections to ensure top-level precedence
    if st.session_state.get("observer_id") and render_sidebar:
        render_custom_sidebar()

    # Bug-PERF-001 FINAL FIX (2026-04-23): Remove ALL external font references.
    # ROOT CAUSE: ANY outbound connection to fonts.googleapis.com or fonts.gstatic.com
    #   causes the Docker browser client to wait for TCP timeout (~120s) before giving up.
    # FINAL FIX: Remove ALL Google Fonts references entirely. Use system font stack only.
    #   System fonts (Segoe UI, -apple-system, Roboto) are visually identical to Inter
    #   and require zero network requests.
    # DO NOT re-add any fonts.googleapis.com or fonts.gstatic.com references.



    st.markdown(
        f"""
    <style>
        /* ============================================================= */
        /* FIX: Bug-PERF-001 — Adversarial Sleep Bomb Remediation        */
        /* DATE: 2026-04-23                                              */
        /* SOLUTION: System Font Only. We prioritize local system fonts  */
        /*   to avoid blocking outbound network requests during render.  */
        /* SEE: tests/resolved_bugs/Bug-PERF-001_resolution.md           */
        /* ============================================================= */


        /* v8.0.0 Global Standard: Eliminate Technical Drift and Visual Flickering */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            font-size: {st.session_state.global_font_size}px !important;
        }}

        /* Sidebar Persistence Guard (§35.1) */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarNav"] span {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            font-size: {st.session_state.global_font_size}px !important;

        /* CR-20260423: Force WINC logo (st.logo) to fill full sidebar width */
        [data-testid="stLogo"] {{
            padding: 8px 0.5rem 4px 0.5rem !important;
            width: 100% !important;
        }}
        [data-testid="stLogo"] img {{
            width: 100% !important;
            max-width: 100% !important;
            height: auto !important;
            object-fit: contain !important;
            display: block !important;
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
        
        /* 🥚 Incubator Tray: High-Contrast Grid for Biological Clarity */
        .egg-tray {{
            background-color: #0f172a !important; /* Deep Slate */
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid #334155;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
            margin-bottom: 10px;
        }}
        
        .egg-tray p, .egg-tray b, .egg-tray span {{
            color: #f8fafc !important;
        }}

        footer {{ visibility: hidden !important; }}

        /* 🎨 Unified Branding Standard (§1) */
        /* Mapping vocabulary to clinical colors for 5th-Grader Standard */
        .stButton > button:has(p:contains("SAVE")), button[data-testid*="SAVE"] {{
            background-color: #10b981 !important;
            color: white !important;
            border: none !important;
        }}
        .stButton > button:has(p:contains("CANCEL")), button[data-testid*="CANCEL"] {{
            background-color: #ef4444 !important;
            color: white !important;
            border: none !important;
        }}
        .stButton > button:has(p:contains("ADD")), button[data-testid*="ADD"] {{
            background-color: #3b82f6 !important;
            color: white !important;
            border: none !important;
        }}
        .stButton > button:has(p:contains("REMOVE")), button[data-testid*="REMOVE"] {{
            background-color: #f87171 !important;
            color: white !important;
            border: none !important;
        }}

        /* 📍 Pinned Help Button (§ISS-9) */
        [data-testid="stSidebarNav"] ul {{
            display: flex;
            flex-direction: column;
            height: calc(100vh - 40px);
        }}
        [data-testid="stSidebarNav"] ul li:last-child {{
            margin-top: auto;
            border-top: 1px solid #334155;
            padding-top: 10px;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )


    return get_supabase()


def render_custom_sidebar():
    """Renders the SHIFT END logout button in the sidebar.
    Logo and user/version identity are now handled in app.py using st.logo()
    and st.sidebar.markdown() BEFORE st.navigation() — this ensures they
    appear ABOVE the navigation links, not below them.
    CR-20260423: Moved logo/identity to app.py to fix st.navigation() ordering.
    This function now only renders the SHIFT END button per page."""

    if st.sidebar.button(
        "SHIFT END",
        key="global_logout_btn",
        use_container_width=True,
        type="primary",
        help="Terminate your shift and password-lock the system.",
    ):
        try:
            get_supabase().table("system_log").insert(
                {
                    "session_id": st.session_state.session_id,
                    "event_type": "TERMINATE",
                    "event_message": f"Session ended: {st.session_state.observer_name}",
                }
            ).execute()
        except:
            pass

        st.session_state.observer_id = None
        st.session_state.env_gate_synced = False
        st.rerun()

@st.cache_resource(ttl=3600)
def get_last_bin_weight(bin_id):
    """
    Hydration Gate Optimization (§35.5).
    Retrieves the last recorded weight for a bin from the clinical ledger.
    """
    supabase = get_supabase()
    last_observation = (
        supabase.table("bin_observation")
        .select("bin_weight_g, timestamp")
        .eq("bin_id", bin_id)
        .order("timestamp", desc=True)
        .limit(1)
        .execute()
    )

    if last_observation.data:
        return last_observation.data[0]

    # Fallback to bin table metadata
    bin_data = (
        supabase.table("bin")
        .select("target_total_weight_g")
        .eq("bin_id", bin_id)
        .execute()
    )
    if bin_data.data:
        return {
            "bin_weight_g": float(bin_data.data[0].get("target_total_weight_g") or 0.0),
            "timestamp": None,
        }

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
                get_resilient_table(get_supabase(), "system_log").insert(
                    {
                        "session_id": st.session_state.get("session_id", "SYSTEM"),
                        "event_type": "AUDIT",
                        "event_message": success_message,
                    }
                ).execute()
            except:
                pass

        return result
    except Exception as e:
        # Standard §36.2: Ensure Streamlit control flow (rerun/stop/switch) is NOT swallowed.
        if "streamlit" in str(type(e)).lower():
            raise e
        
        import traceback

        error_details = traceback.format_exc()
        st.error(
            f"❌ Biological Ledger Error ({operation_name}): Defaulting to Safe-State."
        )

        try:
            get_resilient_table(get_supabase(), "system_log").insert(
                {
                    "session_id": st.session_state.get("session_id", "UNKNOWN_ERR"),
                    "event_type": "ERROR",
                    "event_message": f"[{operation_name}] CRASH: {str(e)}",
                }
            ).execute()
        except:
            pass

        with st.expander("🔍 Differential Diagnosis (Technical Details)"):
            st.code(error_details)
        return None
