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
        
        # Inject Print-Specific CSS for properly paged physical copies
        st.markdown("""
            <style>
            @media print {
                [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], footer {
                    display: none !important;
                }
                .main .block-container {
                    padding: 0 !important;
                    max-width: 100% !important;
                }
                div[style*="page-break-after: always"] {
                    page-break-after: always !important;
                    display: block;
                    height: 0;
                }
                body {
                    color: black !important;
                    background-color: white !important;
                }
                img {
                    max-width: 100% !important;
                    page-break-inside: avoid;
                }
            }
            </style>
        """, unsafe_allow_html=True)

        import re
        import base64

        def get_image_base64(path):
            try:
                # Resolve the relative path in the MD file to an absolute path on disk
                # MD says: ../../assets/manual/img.png
                # But from vault_views/8_Help.py, the path relative to CWD (root) is: assets/manual/img.png
                
                # Strip leading relative dots if present
                clean_path = path.replace("../../", "").replace("../", "")
                full_path = os.path.join(os.getcwd(), clean_path)
                
                if os.path.exists(full_path):
                    with open(full_path, "rb") as image_file:
                        return f"data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
                return path # Fallback
            except:
                return path

        # Find all local image links and swap them for Base64 strings for robust rendering
        image_pattern = r'!\[(.*?)\]\((.*?)\)'
        manual_content = re.sub(image_pattern, lambda m: f'![{m.group(1)}]({get_image_base64(m.group(2))})', manual_content)

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
