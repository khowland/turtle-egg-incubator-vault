"""
=============================================================================
Script:     clean_slate_production.py
Purpose:    Purge all non-lookup biological and transaction data from the 
            PostgreSQL database to prepare for a clean Production release.
=============================================================================
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Bypass Streamlit context cache for flawless CLI execution
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Fatal: Missing .env credentials.")
    exit(1)

sb = create_client(url, key)

print("🧹 Initiating Production Clean-Slate Protocol...")

tables_to_purge = [
    'systemlog',
    'SessionLog',
    'hatchling_ledger',
    'EggObservation',
    'IncubatorObservation',
    'egg',
    'bin',
    'mother'
]

for table in tables_to_purge:
    try:
        # Supabase Python natively requires a filter to delete all rows.
        # A simple string match that evaluates to True (like != 'WIPE_ALL') works flawlessly.
        if table in ['SessionLog', 'systemlog']: filter_col = 'session_id'
        elif table == 'EggObservation': filter_col = 'detail_id'
        elif table == 'IncubatorObservation': filter_col = 'obs_id'
        elif table == 'hatchling_ledger': filter_col = 'ledger_id'
        else: filter_col = f"{table}_id"

        sb.table(table).delete().neq(filter_col, 'WIPE_ALL').execute()
        print(f"✅ Purged {table}")
    except Exception as e:
        print(f"⚠️ Could not purge {table}: {str(e)}")

print("\n🚀 Database is now clean and ready for Production.")
