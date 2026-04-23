# =============================================================================
# ⚠️  QUARANTINED — DO NOT EXECUTE ⚠️
# =============================================================================
# Date: 2026-04-23
# Reason: This script dynamically rewrites production source files at runtime
#         using regex substitution and injects backdoor hooks into Intake UI.
#         It also contains HARDCODED DATABASE CREDENTIALS in plaintext.
#         Identified during Bug-PERF-001 adversarial sleep bomb investigation
#         as a potential reintroduction vector for adversarial code.
#
# Security Issues Found:
#   1. Lines 6-14:  Regex-rewrites all e2e test files without backup
#   2. Lines 17-18: Hardcoded DB host and password in plaintext
#   3. Lines 39-47: Injects a "FORENSIC" backdoor hook into 2_New_Intake.py
#
# This file is preserved for forensic reference only.
# See: tests/resolved_bugs/Bug-PERF-001_resolution.md
# See: docs/QA_Troubleshooting_Log.md
# =============================================================================
import sys
print("❌ QUARANTINED: This script has been disabled for security reasons.")
print("   See: tests/resolved_bugs/Bug-PERF-001_resolution.md")
sys.exit(1)

import os
import psycopg2
import re

print("1. Fixing Ports and Playwright Data Grid Interactions...")
for f in os.listdir('tests/e2e_playwright'):
    if f.endswith('.py'):
        path = os.path.join('tests/e2e_playwright', f)
        with open(path, 'r') as file:
            content = file.read()
        content = re.sub(r'850[0-9]', '8501', content)
        content = content.replace('page.get_by_label("Initial Mass (g)").fill("15.5")', '# Bypassed canvas grid via backend hook')
        with open(path, 'w') as file:
            file.write(content)

print("2. Applying Database Migrations (Schema Changes)...")
db_password = os.environ.get('SUPABASE_DB_PASSWORD', 'Spr1ng4wd/Int0/Action26!')
host = 'db.kxfkfeuhkdopgmkpdimo.supabase.co'
conn_str = f"dbname='postgres' user='postgres' host='{host}' password='{db_password}' port='5432'"
try:
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    cursor = conn.cursor()
    with open('supabase_db/migrations/v8_1_24_ADD_CLINICAL_METADATA.sql', 'r') as f:
        cursor.execute(f.read())
    print(" => Applied metadata migration (JSONB).")
    with open('supabase_db/migrations/v8_1_25_SUPPLEMENTAL_INTAKE.sql', 'r') as f:
        cursor.execute(f.read())
    print(" => Applied supplemental RPC migration.")
    conn.close()
except Exception as e:
    print(" => Migration error (might already exist):", e)

print("3. Injecting E2E Canvas Bypass Hook into Intake UI...")
ui_path = 'vault_views/2_New_Intake.py'
with open(ui_path, 'r') as f:
    ui_code = f.read()

backdoor = """        # Extended Validation for hardened requirements
        if finder_name.startswith("FORENSIC"):
            for r in st.session_state.bin_rows:
                r["mass"] = 15.5
"""
if 'startswith("FORENSIC")' not in ui_code:
    ui_code = ui_code.replace('# Extended Validation for hardened requirements', backdoor)
    with open(ui_path, 'w') as f:
        f.write(ui_code)
print(" => Hook injected.")
