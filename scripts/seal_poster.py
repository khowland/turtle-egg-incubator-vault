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
    <!-- Background Frame -->
    <rect width="612" height="792" fill="#2c3e50" />
    <rect x="15" y="15" width="582" height="762" fill="white" />
    
    <!-- The Illustration (Base64) -->
    <image xlink:href="data:image/png;base64,{img_b64}" x="30" y="180" width="552" height="430" preserveAspectRatio="xMidYMid slice" />
    
    <!-- Header Bubble -->
    <rect x="60" y="40" width="492" height="120" rx="30" fill="white" stroke="#27ae60" stroke-width="6" />
    
    <!-- Title Text -->
    <text x="306" y="105" text-anchor="middle" font-family="Arial Black, sans-serif" font-size="54" fill="#27ae60">WINC</text>
    <text x="306" y="140" text-anchor="middle" font-family="Arial, sans-serif" font-weight="bold" font-size="20" fill="#2c3e50">TURTLE EGG INCUBATION SYSTEM</text>
    
    <!-- Footer Block (Removed Center Block, replaced with small right-aligned text) -->
    <rect x="0" y="740" width="612" height="52" fill="white" />
    <rect x="0" y="740" width="612" height="4" fill="#27ae60" />
    
    <!-- Credit Text (Lower Right, Conservative) -->
    <text x="582" y="770" text-anchor="end" font-family="Arial, sans-serif" font-size="11" fill="#2c3e50">Developed by Kevin Howland</text>
    <text x="582" y="785" text-anchor="end" font-family="Arial, sans-serif" font-size="9" fill="#7f8c8d">it2howland@gmail.com | v10.5.1</text>
    
    <!-- Version/Title Note (Lower Left) -->
    <text x="30" y="775" text-anchor="start" font-family="Arial, sans-serif" font-weight="bold" font-size="12" fill="#27ae60">OFFICIAL OPERATOR'S MANUAL</text>
    
    <!-- Version Badge -->
    <polygon points="520,0 580,0 580,80 550,65 520,80" fill="#f1c40f" stroke="black" stroke-width="2" />
    <text x="550" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-weight="800" font-size="10" fill="#2c3e50">WINC</text>
    <text x="550" y="55" text-anchor="middle" font-family="Arial, sans-serif" font-weight="800" font-size="12" fill="#2c3e50">V10.5</text>
</svg>"""

with open(SVG_PATH, "w") as f:
    f.write(svg_content)

print(f"✅ Success: Locked image into {SVG_PATH}")
