"""
=============================================================================
Module:        vault_views/8_Help.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35, §36]
Upstream:      None (Entry point or dynamic)
Downstream:    utils.bootstrap
Use Cases:     [Pending - Describe practical usage here]
Inputs:        docs/operator/OPERATOR_MANUAL.md
Outputs:       st.markdown
Description:   In-app clinical manual for staff reference and onboarding.
=============================================================================
"""

import streamlit as st
import os
from utils.bootstrap import bootstrap_page
from utils.performance import track_view_performance

# 1. Page Initialization
supabase = bootstrap_page("Help", "📚")

with track_view_performance("Help"):
    st.title("📚 Help")

    # 2. Render Path Detection
    # We use absolute project root paths now
    manual_path = os.path.join(os.getcwd(), "docs", "user", "OPERATOR_MANUAL.md")

    try:
        if os.path.exists(manual_path):
            with open(manual_path, "r", encoding="utf-8") as f:
                manual_content = f.read()

            # Inject Print-Specific CSS for properly paged physical copies
            st.markdown(
                """
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
            """,
                unsafe_allow_html=True,
            )

            import re
            import base64
            from pathlib import Path

            # Core Path Resolution (§v9.0.1 Migration)
            ROOT_DIR = Path(__file__).parent.parent

            def get_image_base64(path_str):
                try:
                    # Normalize path separators and remove relative dots
                    clean_path = (
                        path_str.replace("\\", "/").replace("../../", "").replace("../", "")
                    )
                    full_path = ROOT_DIR / clean_path

                    if full_path.exists():
                        ext = full_path.suffix.lower()
                        mime = "image/png"
                        if ext == ".svg":
                            mime = "image/svg+xml"
                        elif ext in [".jpg", ".jpeg"]:
                            mime = "image/jpeg"

                        with open(full_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode()
                            return f"data:{mime};base64,{b64}"
                    return path_str
                except Exception as e:
                    return path_str

            # 1. Update Markdown Image Syntax: ![alt](path)
            md_pattern = r"!\[(.*?)\]\((.*?)\)"
            manual_content = re.sub(
                md_pattern,
                lambda m: f"![{m.group(1)}]({get_image_base64(m.group(2))})",
                manual_content,
            )

            # 2. Update HTML Image Syntax: <img src="path" ...>
            html_pattern = r'<img\s+[^>]*src="([^"]+)"'
            manual_content = re.sub(
                html_pattern,
                lambda m: m.group(0).replace(m.group(1), get_image_base64(m.group(1))),
                manual_content,
            )

            st.markdown(manual_content, unsafe_allow_html=True)
        else:
            st.warning(
                "⚠️ Manual file not found at expected location: /docs/user/OPERATOR_MANUAL.md"
            )
            st.info(
                "Please contact the system administrator to synchronize the documentation design."
            )

    except Exception as e:
        st.error(f"❌ Error loading manual: {str(e)}")

    # 3. Supplemental WINC Resources
    with st.sidebar:
        st.header("🖨️ Clinical Printing")
        # Find the most recent OPERATOR_MANUAL PDF dynamically
        # (avoids hardcoded version strings becoming stale)
        _manual_dir = os.path.join(os.getcwd(), "docs", "user")
        _pdfs = sorted(
            [f for f in os.listdir(_manual_dir) if f.startswith("OPERATOR_MANUAL") and f.endswith(".pdf")],
            reverse=True  # latest version first (lexicographic sort works for v10_x_y)
        )
        if _pdfs:
            _pdf_path = os.path.join(_manual_dir, _pdfs[0])
            with open(_pdf_path, "rb") as f:
                st.sidebar.download_button(
                    label=f"⬇️ Download PDF Manual",
                    data=f,
                    file_name=_pdfs[0],
                    mime="application/pdf",
                    help=f"Download the institutional-grade paged version for physical lab binders. ({_pdfs[0]})"
                )
        else:
            st.sidebar.error("PDF not found. Run: python scripts/generate_clinical_manual_pdf.py")

        st.header("🖇️ Quick Resources")
        st.write("[PostgreSQL Schema](docs/design/db_schema_export.txt)")
        st.write("[System Design Spec](docs/design/SYSTEM_DESIGN_SPEC.md)")
        # CR-20260423-111948: Version display removed; now shown in sidebar header
