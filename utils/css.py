"""
=============================================================================
Module:     utils/css.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    Aero-Shield CSS - High-performance UI hardening and branding.
=============================================================================
"""

BASE_CSS = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebarNav"] {display: none;}

    /* Aero-Shield: Wipe out Ask AI buttons and Tracebacks */
    [data-testid="stException"] button, 
    [data-testid="stException"] a, 
    [data-testid="stException"] summary {
        display: none !important;
    }
    
    /* Hide technical traceback details */
    [data-testid="stException"] .st-ae, 
    [data-testid="stException"] pre {
        display: none !important;
    }

    .main { background-color: #0F172A; color: #F8FAFC; }
    .stButton > button { height: 60px !important; border-radius: 12px !important; }
</style>
"""
