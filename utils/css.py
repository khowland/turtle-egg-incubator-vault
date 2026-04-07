BASE_CSS = """
<style>
    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* VIVID-NAV: Force the sidebar navigation to be visible */
    section[data-testid="stSidebar"] div[data-testid="stSidebarNav"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Standard WINC Theme */
    .main { background-color: #0F172A; color: #F8FAFC; }
</style>
"""
