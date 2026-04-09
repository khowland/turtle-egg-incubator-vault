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
    'eggobservation',
    'incubatorobservation',
    'hatchling_ledger',
    'egg',
    'bin',
    'mother',
    'systemlog',
    'sessionlog'
]

for table in tables_to_purge:
    try:
        if table in ['sessionlog', 'systemlog']: 
            filter_col = 'session_id' if table == 'sessionlog' else 'log_id'
        elif table == 'eggobservation': filter_col = 'detail_id'
        elif table == 'incubatorobservation': filter_col = 'obs_id'
        elif table == 'hatchling_ledger': filter_col = 'id'
        else: filter_col = f"{table}_id"

        # Determine if ID column is Integer, UUID, or String
        if filter_col in ['detail_id', 'log_id', 'ledger_id']:
            sb.table(table).delete().gt(filter_col, -1).execute()
        elif table == 'hatchling_ledger':
            # Use a dummy UUID that won't exist
            sb.table(table).delete().not_.eq('id', '00000000-0000-0000-0000-000000000000').execute()
        else:
            sb.table(table).delete().neq(filter_col, 'WIPE_ALL').execute()
            
        print(f"✅ Purged {table}")
    except Exception as e:
        print(f"⚠️ Could not purge {table}: {str(e)}")

print("\n🚀 Database is now clean and ready for Production.")
