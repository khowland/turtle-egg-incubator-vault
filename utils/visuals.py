"""
=============================================================================
Module:        utils/visuals.py
Project:       WINC Incubator System
Requirement:   Matches Standard [§35.1]
Dependencies:  None
Inputs:        stage, chalk, vasc, status, selected
Outputs:       Base64 SVG String
Description:   Biological SVG Loader for custom high-definition icons.
=============================================================================
"""
import base64
import os

ASSET_PATH = "assets/icons"

def render_egg_icon(stage, chalk, vasc, status, selected=False):
    """Loads and returns a high-definition biological SVG from assets."""
    # Mapping stages to custom files
    icon_map = {
        "S0": "egg_s1.svg",
        "S1": "egg_s1.svg",
        "S2": "egg_s2.svg",
        "S3": "egg_s3.svg",
        "S4": "egg_s3.svg", # S4 uses chalking icon if no specific S4 exist
        "S5": "egg_s4.svg",
        "S6": "egg_s5.svg"
    }
    
    filename = icon_map.get(stage, "egg_s1.svg")
    filepath = os.path.join(ASSET_PATH, filename)
    
    if not os.path.exists(filepath):
        # Fallback to a minimal SVG if file missing
        return "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGVsbGlwc2UgY3g9IjMwIiBjeT0iNDAiIHJ4PSIyMCIgcnk9IjI4IiBmaWxsPSIjZGRkIiAvPjwvc3ZnPg=="

    with open(filepath, 'r') as f:
        svg_content = f.read()

    # Dynamic Customization (Injecting Border/Status)
    # 1. Selection State (Blue Border)
    if selected:
        svg_content = svg_content.replace('stroke="#D1D5DB"', 'stroke="#3b82f6"')
        svg_content = svg_content.replace('stroke-width="1"', 'stroke-width="3"')
    
    # 2. Inactive State (Grey Tone)
    if status != "Active":
        svg_content = svg_content.replace('#FFFDD0', '#D1D5DB')
        svg_content = svg_content.replace('#FFFFFF', '#E5E7EB') # Dim bands/veins

    b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"
