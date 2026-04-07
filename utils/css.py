BASE_CSS = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Force Sidebar Nav to be visible */
    [data-testid="stSidebarNav"] { 
        display: block !important; 
        visibility: visible !important;
    }

    .main { 
        background-color: #0F172A; 
        color: #F8FAFC; 
    }
</style>
"""