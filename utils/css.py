"""
=============================================================================
Module:     utils/css.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Design tokens and raw CSS strings for the Bento-Glass 2026
            UI system. Implements Section 3 of Requirements.md.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

# SECTION: Design Tokens & CSS Strings

# Titanium High-Contrast Base Styling
BASE_CSS = """
<style>
    /* Import Inter from Google Fonts per Spec §3.1 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800;900&display=swap');

    .stApp {
        background-color: #020617 !important; /* Deep Space Navy */
        color: #FFFFFF !important; /* Titanium White */
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidebar Theming §4 */
    [data-testid="stSidebar"] {
        background-color: #050810 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebarNav"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important; 
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }

    /* Glass Card Component §3.2 */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* Emergency Pulse Animation §3.3 */
    @keyframes pulse-danger {
        0%, 100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
        50% { box-shadow: 0 0 24px rgba(239, 68, 68, 0.8); }
    }
    .alert-critical {
        animation: pulse-danger 1.5s ease-in-out infinite;
        border: 2px solid #EF4444 !important;
    }

    /* Wet-Hand Buttons §3.1 */
    div.stButton > button {
        background-color: #10B981 !important; /* Emerald */
        color: #FFFFFF !important; /* White Text */
        border: 2px solid #34D399 !important;
        border-radius: 12px !important;
        height: 70px !important; /* Wet-Hand Height */
        width: 100% !important;
        font-weight: 900 !important;
        font-size: 1.2rem !important;
        box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        background-color: #34D399 !important;
    }

    /* Input Fields */
    .stTextInput input, .stNumberInput input, div[data-baseweb="select"] > div {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }

    /* Utility: Hide Defaults */
    #MainMenu, footer { visibility: hidden; }
</style>
"""
