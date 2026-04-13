"""
=============================================================================
Module:        utils/visuals.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35.1]
Upstream:      vault_views/3_Observations.py
Downstream:    None
Use Cases:     [Pending - Describe practical usage here]
Inputs:        stage, chalk, vasc, status, selected
Outputs:       Base64 SVG String
Description:   Biological SVG Loader with Dynamic Color Correction.
=============================================================================
"""

import base64
import os

ASSET_PATH = "assets/icons"


def render_egg_icon(stage, chalk, vasc, status, selected=False):
    """Loads and returns a high-definition biological SVG with color correction."""
    # Mapping stages to custom files
    icon_map = {
        "S0": "egg_s1.svg",
        "S1": "egg_s1.svg",
        "S2": "egg_s2.svg",
        "S3": "egg_s3.svg",
        "S4": "egg_s3.svg",
        "S5": "egg_s4.svg",
        "S6": "egg_s5.svg",
    }

    filename = icon_map.get(stage, "egg_s1.svg")
    filepath = os.path.join(ASSET_PATH, filename)

    if not os.path.exists(filepath):
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGVsbGlwc2UgY3g9IjMwIiBjeT0iNDAiIHJ4PSIyMCIgcnk9IjI4IiBmaWxsPSIjZGRkIiAvPjwvc3ZnPg=="

    with open(filepath, "r") as f:
        svg_content = f.read()

    # Dynamic Color Correction for Visibility (§v8.1.3 Updates)
    # Shell Color: From Cream (#FFFDD0) to Natural Tan (#E3C586)
    target_shell = "#E3C586" if status == "Active" else "#D1D5DB"
    svg_content = svg_content.replace("#FFFDD0", target_shell)

    # 1. Selection State (Blue Border)
    if selected:
        svg_content = svg_content.replace('stroke="#D1D5DB"', 'stroke="#3b82f6"')
        svg_content = svg_content.replace('stroke-width="1"', 'stroke-width="3"')

    # 2. Inactive State (Grey Tone)
    if status != "Active":
        svg_content = svg_content.replace("#FFFFFF", "#E5E7EB")

    b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"
