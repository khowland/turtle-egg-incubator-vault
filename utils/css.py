"""
=============================================================================
Module:     utils/css.py
Project:    WINC Incubator Vault v6.3.2
Purpose:    Aero-Shield CSS - Surgical UI hardening.
=============================================================================
"""

BASE_CSS = """
<style>
    /* 1. Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 2. Surgical Aero-Shield: Hide ONLY the AI Help buttons in error blocks */
    /* We avoid hiding 'button' or 'a' globally to protect the Sidebar Navigation */
    [data-testid="stException"] button[title*="Ask"], 
    [data-testid="stException"] a[href*="google"], 
    [data-testid="stException"] a[href*="openai"] {
        display: none !important;
    }
    
    /* Hide technical traceback details but keep the error message visible */
    [data-testid="stException"] pre, 
    [data-testid="stException"] .st-ae {
        display: none !important;
    }

    /* 3. WINC Theme & Touch Targets */
    .main { background-color: #0F172A; color: #F8FAFC; }
    
    /* Large buttons for field use, but ONLY for standard buttons, not nav links */
    div[data-testid="stButton"] > button {
        height: 60px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
</style>
"""
