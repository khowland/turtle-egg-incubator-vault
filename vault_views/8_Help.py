"""
=============================================================================
Module:        vault_views/8_Help.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Dependencies:  utils.bootstrap
Inputs:        docs/operator/OPERATOR_MANUAL.md
Outputs:       st.markdown
Description:   In-app clinical manual for staff reference and onboarding.
=============================================================================
"""

import streamlit as st
import os
from utils.bootstrap import bootstrap_page

# 1. Page Initialization
supabase = bootstrap_page("Help & Manual", "📚")
st.title("📚 Clinical Help & Manual")

# 2. Render Path Detection
# We use absolute project root paths now
manual_path = os.path.join(os.getcwd(), "docs", "user", "OPERATOR_MANUAL.md")

try:
    if os.path.exists(manual_path):
        with open(manual_path, "r", encoding="utf-8") as f:
            manual_content = f.read()
        
        # Clean up absolute file links if they exist for cleaner UI
        manual_content = manual_content.replace("file:///c:/dev/projects/turtle-db/", "")
        
        st.markdown(manual_content, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Manual file not found at expected location: /docs/user/OPERATOR_MANUAL.md")
        st.info("Please contact the system administrator to synchronize the documentation design.")

except Exception as e:
    st.error(f"❌ Error loading manual: {str(e)}")

# 3. Supplemental WINC Resources
with st.sidebar:
    st.header("🖇️ Quick Resources")
    st.write("[PostgreSQL Schema](docs/design/db_schema_export.txt)")
    st.write("[System Design Spec](docs/design/SYSTEM_DESIGN_SPEC.md)")
    st.divider()
    st.caption("WINC-Vault v8.0.0 (2026 Season)")
