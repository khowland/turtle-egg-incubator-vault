"""
=============================================================================
Module:        utils/visuals.py
Project:       Incubator Vault v8.1.3 — WINC (Clinical Sovereignty Edition)
Requirement:   Matches Standard [§35.1]
Dependencies:  None
Inputs:        stage, chalk, vasc, status, selected
Outputs:       Base64 SVG String
Description:   Biological SVG Rendering Engine for high-contrast grid visuals.
=============================================================================
"""
import base64

def render_egg_icon(stage, chalk, vasc, status, selected=False):
    """Generates a high-definition biological SVG for the grid."""
    border_color = "#3b82f6" if selected else "#d1d5db"
    border_width = "3" if selected else "1"
    
    # User Input Normalization
    chalk_val = int(chalk) if chalk is not None else 0
    chalk_op = (chalk_val / 2.0) * 0.9 if status == "Active" else 0.2
    
    # 1. Base Geometry: Realistic Ovoid Shell (Cream / Off-White)
    shell_color = "#FFFDD0" if status == "Active" else "#D1D5DB"
    egg_path = f'<path d="M30 15 C15 15 10 35 10 50 C10 65 20 75 30 75 C40 75 50 65 50 50 C50 35 45 15 30 15 Z" fill="{shell_color}" stroke="{border_color}" stroke-width="{border_width}" />'
    
    # 2. Chalking Band (The Equator)
    band = ""
    if chalk_val > 0:
        band = f'<path d="M10 45 Q30 42 50 45 L50 55 Q30 52 10 55 Z" fill="white" fill-opacity="{chalk_op}" />'
        
    # 3. Vascularity (Realistic Branching Veins)
    veins = ""
    if vasc and status == "Active":
        veins = '<g stroke="#D00000" stroke-width="1.2" fill="none" opacity="0.8"><path d="M30 45 L30 30 M30 35 L22 25 M30 38 L38 28 M22 25 L18 20 M38 28 L42 22" /></g>'
        
    # 4. Stage Overlays (Pipping & Hatching)
    overlay = ""
    if stage == "S5":
        # Multi-point star crack (Pipping)
        overlay = '<path d="M25 35 L35 45 M35 35 L25 45 M30 32 L30 48 M22 40 L38 40" stroke="#333" stroke-width="1.5" />'
    elif stage == "S6":
        # Jagged Broken Shell (Lower half only) - "The Hatched Look"
        egg_path = '<path d="M10 50 L15 45 L20 50 L25 42 L30 50 L35 44 L40 50 L45 46 L50 50 L50 65 C50 75 40 85 30 85 C20 85 10 75 10 65 Z" fill="#E5E7EB" stroke="#9CA3AF" />'
        band = ""

    # Final SVG Assembly
    svg = f"""<svg width="60" height="90" viewBox="0 0 60 90" xmlns="http://www.w3.org/2000/svg">{egg_path}{band}{veins}{overlay}</svg>"""
    
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"
