import base64
from pathlib import Path

# Paths
ROOT_DIR = Path("c:/dev/projects/turtle-db")
IMG_PATH = ROOT_DIR / "assets/manual/cover.png"
SVG_PATH = ROOT_DIR / "assets/manual/poster_cover.svg"

# Encode Image
with open(IMG_PATH, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Layout Settings
font_title = "Arial Black, sans-serif"
font_regular = "Arial, sans-serif"
color_main = "#ffffff"  # High contrast white for dark pond/grass bg
color_accent = "#2ecc71" # Clinical Green

svg_content = f"""<svg width="612" height="792" viewBox="0 0 612 792" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <!-- Background Frame -->
    <rect width="612" height="792" fill="#2c3e50" />
    
    <!-- The Illustration (Full Bleed) -->
    <image xlink:href="data:image/png;base64,{img_b64}" x="0" y="0" width="612" height="792" preserveAspectRatio="xMidYMid slice" />
    
    <!-- TWO-LINE TITLE (Flat contrasting, Large) -->
    <text x="306" y="90" text-anchor="middle" font-family="{font_title}" font-size="38" fill="{color_main}">WINC TURTLE EGG INCUBATION</text>
    <text x="306" y="140" text-anchor="middle" font-family="{font_title}" font-size="38" fill="{color_main}">AND HATCHING SYSTEM</text>
    
    <!-- OFFICIAL LABEL (Center Bottom) -->
    <text x="306" y="740" text-anchor="middle" font-family="{font_title}" font-size="18" fill="{color_main}">OFFICIAL OPERATOR'S MANUAL</text>
    
    <!-- CREDITS (Lower Right, Conservative) -->
    <text x="580" y="765" text-anchor="end" font-family="{font_regular}" font-size="12" font-weight="bold" fill="{color_main}">Developed by Kevin Howland</text>
    <text x="580" y="780" text-anchor="end" font-family="{font_regular}" font-size="10" fill="{color_main}">it2howland@gmail.com | v10.5.1</text>
    
</svg>"""

with open(SVG_PATH, "w") as f:
    f.write(svg_content)

print(f"✅ Success: Locked Final Master into {SVG_PATH}")
