#!/usr/bin/env python3
"""ORDER-003: Vision QA Runner — Analyze turtle_db_welcome.png using local Gemma vision model."""
import requests, base64, json, sys
from datetime import datetime

SCREENSHOT_PATH = "/a0/usr/workdir/A2A/screenshots/turtle_db_welcome.png"
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
OUTPUT_PATH = "/a0/usr/workdir/A2A/RESPONSE.md"
MODEL = "gemma4:e4b"

PROMPT = """You are a QA vision tester analyzing a Streamlit web application screenshot for TURTLE DATABASE QUALITY ASSURANCE.

Analyze this screenshot and report:

1. PAGE IDENTITY: What is the visible page title? What app name and version is shown?

2. UI ELEMENTS (with approximate pixel coordinates):
   - List ALL buttons visible. For each button, provide: label text, approximate (x,y) center coordinates, and color.
   - List ALL text inputs/fields visible.
   - List ALL select boxes / dropdowns visible.
   - List ANY data tables or grids visible.

3. USER NAME DETECTION: Is a user name displayed? Who is logged in?

4. VISUAL DEFECTS: Are there any misalignments, overlapping elements, missing labels, poor contrast, or rendering artifacts?

5. CRITICAL QA CHECK: Does the START button appear correctly positioned and clickable? Would a pixel-coordinate click at its center successfully activate it?

6. SCREENSHOT METADATA: What are the overall dimensions? Is the page loading properly?

Output format: Use numbered sections matching 1-6 above. Be precise with coordinates."""

try:
    with open(SCREENSHOT_PATH, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    resp = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": PROMPT,
        "images": [img_b64],
        "stream": False
    }, timeout=90)

    response_text = resp.json().get("response", "NO RESPONSE")

    report = f"""# 📬 MSI Stealth Response
**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC-5')}
**Order**: ORDER-003

## ORDER-003: Vision QA Report — Turtle-DB Welcome Page

{response_text}

---
## MSI Status
- Vision Model: {MODEL}
- Ollama API: reachable
- ORDER-003: COMPLETE ✅
"""

    with open(OUTPUT_PATH, "w") as f:
        f.write(report)

    print("✅ ORDER-003 COMPLETE — Report saved to", OUTPUT_PATH)
    print(response_text[:500])

except Exception as e:
    print(f"❌ FAILED: {e}")
    with open(OUTPUT_PATH, "w") as f:
        f.write(f"# 📬 MSI Stealth Response\n**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC-5')}\n**Order**: ORDER-003 FAILED ❌\n\nError: {e}\n")
    sys.exit(1)
