import base64
from pathlib import Path

# Paths
ROOT_DIR = Path("c:/dev/projects/turtle-db")
IMG_PATH = ROOT_DIR / "assets/manual/cover.png"
SVG_PATH = ROOT_DIR / "assets/manual/poster_cover.svg"

# Encode Image
with open(IMG_PATH, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

svg_content = f"""<svg width="612" height="792" viewBox="0 0 612 792" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs>
        <!-- Stylized Title Gradient -->
        <linearGradient id="titleGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2ecc71;stop-opacity:1" />
        </linearGradient>
        
        <!-- Text Shadow for Readability -->
        <filter id="textShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
            <feOffset dx="2" dy="2" result="offsetblur" />
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.5" />
            </feComponentTransfer>
            <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
            </feMerge>
        </filter>
    </defs>

    <!-- The Master Artwork (Full Bleed) -->
    <image xlink:href="data:image/png;base64,{img_b64}" x="0" y="0" width="612" height="792" preserveAspectRatio="xMidYMid slice" />
    
    <!-- DESIGNED TITLE BLOCK -->
    <g filter="url(#textShadow)">
        <text x="306" y="85" text-anchor="middle" font-family="Verdana, Geneva, sans-serif" font-weight="900" font-size="36" fill="url(#titleGrad)" stroke="#1b5e20" stroke-width="1.5">WINC TURTLE EGG INCUBATION</text>
        <text x="306" y="135" text-anchor="middle" font-family="Verdana, Geneva, sans-serif" font-weight="900" font-size="34" fill="url(#titleGrad)" stroke="#1b5e20" stroke-width="1.5">&amp; HATCHING SYSTEM</text>
    </g>
    
    <!-- OFFICIAL STATUS BAR -->
    <rect x="156" y="715" width="300" height="30" rx="15" fill="rgba(44, 62, 80, 0.85)" stroke="#ffffff" stroke-width="1" />
    <text x="306" y="736" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="14" fill="#ffffff" letter-spacing="2">OFFICIAL USER MANUAL</text>
    
    <!-- CONSERVATIVE SIGNATURE -->
    <text x="590" y="770" text-anchor="end" font-family="Georgia, serif" font-style="italic" font-size="11" fill="#2c3e50">Developed by Kevin Howland</text>
    <text x="590" y="785" text-anchor="end" font-family="Arial, sans-serif" font-weight="bold" font-size="9" fill="#7f8c8d">VERSION 10.5.2</text>
    
</svg>"""

with open(SVG_PATH, "w") as f:
    f.write(svg_content)

print(f"✅ Success: Applied Designer Typography to {SVG_PATH}")
