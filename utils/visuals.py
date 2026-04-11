"""
=============================================================================
Module:        utils/visuals.py
Project:       Incubator Vault v8.0.0 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35.1]
Dependencies:  None
Inputs:        stage, chalk, vasc, status, selected
Outputs:       Base64 SVG String
Description:   Biological SVG Rendering Engine for high-contrast grid visuals.
=============================================================================
"""
import base64

def render_egg_icon(stage, chalk, vasc, status, selected=False):
    """Generates a high-contrast clinical SVG for the grid."""
    bg_color = "#fefce8" if status == "Active" else "#f3f4f6"
    border_color = "#3b82f6" if selected else "#d1d5db"
    border_width = "3" if selected else "1"
    
    # Chalking Band Opacity (0, 1, 2)
    # v8.0.0: Enforce [0, 1, 2] scale
    chalk_val = int(chalk) if chalk is not None else 0
    chalk_op = (chalk_val / 2.0) * 0.9 if status == "Active" else 0.2
    
    # SVG Paths
    ovoid = '<ellipse cx="30" cy="40" rx="20" ry="28" fill="ENTITY_BG" stroke="ENTITY_BORDER" stroke-width="ENTITY_BW" />'
    ovoid = ovoid.replace("ENTITY_BG", bg_color).replace("ENTITY_BORDER", border_color).replace("ENTITY_BW", border_width)
    
    # Chalking Band (The equator)
    band = ""
    if chalk_val > 0:
        band = f'<rect x="10" y="32" width="40" height="15" rx="5" fill="white" fill-opacity="{chalk_op}" />'
        
    # Vascularity (The "Neural Pulse")
    veins = ""
    if vasc and status == "Active":
        veins = '<path d="M30 30 L25 20 M30 30 L35 20 M30 30 L30 50" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" opacity="0.8" />'
        
    # Stage Overlays
    pip = ""
    if stage == "S5":
        pip = '<path d="M25 25 L35 35 M35 25 L25 35" stroke="black" stroke-width="2" />'
    elif stage == "S6":
        ovoid = '<path d="M10 40 Q30 80 50 40 L50 60 Q30 90 10 60 Z" fill="#e5e7eb" stroke="#9ca3af" />'

    svg = f"""
    <svg width="60" height="80" viewBox="0 0 60 80" xmlns="http://www.w3.org/2000/svg">
        {ovoid}
        {band}
        {veins}
        {pip}
    </svg>
    """
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"
