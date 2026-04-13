"""
=============================================================================
# Script:     clean_slate_production.py
# Purpose:    Purge all non-lookup biological and transaction data from the 
#             PostgreSQL database to prepare for a clean Production release.
# Standard:   Titan Engine Enterprise Standard v7.9.9 (§35)
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

print("🧹 Initiating Production Clean-Slate Protocol (Enterprise §35)...")

# Requirement §35: Standard Singular Snake_case Table Names
tables_to_purge = [
    'egg_observation',
    'bin_observation',
    'hatchling_ledger',
    'egg',
    'bin',
    'mother',
    'system_log',
    'session_log'
]

for table in tables_to_purge:
    try:
        # Standard §35: Contextual Primary Keys
        if table == 'system_log':
            filter_col = 'system_log_id'
        elif table == 'session_log':
            filter_col = 'session_id'
        else:
            filter_col = f"{table}_id"

        print(f"Purging {table} using PK {filter_col}...")

        # Determine if ID column is Integer (BigInt), UUID, or String
        # Standard: System log uses BigInt Identity; Ledger/Identity use UUID; Session/Entities use Text
        if table == 'system_log':
            sb.table(table).delete().gt(filter_col, -1).execute()
        elif table in ['hatchling_ledger', 'bin_observation']:
            # UUID Purge (Match all non-null)
            sb.table(table).delete().neq(filter_col, '00000000-0000-0000-0000-000000000000').execute()
        else:
            # Text/PK Purge
            sb.table(table).delete().neq(filter_col, 'WIPE_ALL').execute()
            
        print(f"✅ Purged {table}")
    except Exception as e:
        print(f"⚠️ Could not purge {table}: {str(e)}")

print("\n🚀 Database is now clean and fully standard-aligned.")
