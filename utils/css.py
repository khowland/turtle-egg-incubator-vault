"""
=============================================================================
Module:     utils/css.py
Project:    Incubator Vault v6.1 — Wildlife In Need Center (WINC)
Purpose:    Design tokens and CSS for the Bento-Glass UI system (§3).
            Mobile-first design for portrait phone use at the incubator.
Author:     Agent Zero (Automated Build)
Modified:   2026-04-06 (Mobile-first rewrite for field staff usability)
=============================================================================
"""

# =============================================================================
# SECTION: Design Tokens & CSS
# Description: Mobile-first CSS with progressive enhancement for desktop.
#              Priority: readability and touch targets on a 360px phone screen
#              held by a busy wildlife staffer wearing wet gloves.
# =============================================================================

BASE_CSS = """
<style>
    /* === FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

    /* === BASE THEME: Dark high-contrast for indoor/outdoor readability === */
    .stApp {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebarNav"] span,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #F1F5F9 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }

    /* === CARDS: Clean containers, no heavy blur on mobile === */
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* === CRITICAL ALERT: Pulsing red border for molding/leaking eggs === */
    @keyframes pulse-danger {
        0%, 100% { box-shadow: 0 0 6px rgba(239, 68, 68, 0.3); }
        50% { box-shadow: 0 0 18px rgba(239, 68, 68, 0.7); }
    }
    .alert-critical {
        animation: pulse-danger 1.5s ease-in-out infinite;
        border: 2px solid #EF4444 !important;
    }

    /* === BUTTONS: Large touch targets for gloved hands === */
    div.stButton > button {
        background-color: #10B981 !important;
        color: #FFFFFF !important;
        border: 2px solid #34D399 !important;
        border-radius: 12px !important;
        height: 60px !important;
        width: 100% !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        background-color: #34D399 !important;
    }

    /* === FORM INPUTS: Dark themed, readable === */
    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #F1F5F9 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 10px !important;
        min-height: 50px !important;
        font-size: 1.05rem !important;
    }

    /* === DROPDOWNS: Enlarged for touch === */
    div[data-baseweb="select"] > div {
        display: flex !important;
        align-items: center !important;
    }

    /* === CHECKBOXES: Enlarged for gloved fingers === */
    .stCheckbox > label {
        padding: 8px 0 !important;
        font-size: 1.05rem !important;
    }

    /* === FORM LABELS: Bold and clear === */
    .stTextInput label, .stSelectbox label,
    .stNumberInput label, .stTextArea label,
    .stCheckbox label, .stToggle label {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #CBD5E1 !important;
    }

    /* === HIDE STREAMLIT CHROME === */
    #MainMenu, footer { visibility: hidden; }

    /* ================================================================
       MOBILE: Portrait phone at the incubator (< 768px)
       Single-column, compact, zero clutter.
       ================================================================ */
    @media (max-width: 768px) {
        /* Force ALL columns to full-width stack */
        [data-testid="column"] {
            width: 100% !important;
            flex: 0 0 100% !important;
            min-width: 100% !important;
        }

        /* Compact cards */
        .glass-card {
            padding: 14px !important;
            border-radius: 12px !important;
            margin-bottom: 12px !important;
        }

        /* Slightly smaller buttons on phone (still large) */
        div.stButton > button {
            height: 56px !important;
            font-size: 1.0rem !important;
        }

        /* Page headings */
        h1 { font-size: 1.4rem !important; }
        h3 { font-size: 1.1rem !important; }
    }

    /* ================================================================
       TABLET: Landscape iPad at the desk (768px - 1024px)
       2-column grid for egg cards.
       ================================================================ */
    @media (min-width: 769px) and (max-width: 1024px) {
        [data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
        }
    }

</style>
"""
