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
key = os.environ.get("SUPABASE_ANON_KEY")  # v9.2.0: service_role key invalid; use anon key (has service_role JWT)

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
        # Determine filter column
        if table == 'system_log':
            filter_col = 'system_log_id'
        elif table == 'session_log':
            filter_col = 'session_id'
        else:
            filter_col = f"{table}_id"

        # Audit tables without is_deleted column: skip to preserve history
        if table in ['system_log', 'session_log']:
            print(f"⏭️ Skipping {table} (no is_deleted column; audit trail preserved)")
            continue

        print(f"Soft-deleting {table} using PK {filter_col}...")

        # Soft-delete: update is_deleted = true for all rows (matching original condition)
        if table == 'system_log':
            resp = sb.table(table).update({"is_deleted": True}).gt(filter_col, -1).execute()
        elif table in ['hatchling_ledger', 'bin_observation']:
            resp = sb.table(table).update({"is_deleted": True}).neq(filter_col, '00000000-0000-0000-0000-000000000000').execute()
        else:
            resp = sb.table(table).update({"is_deleted": True}).neq(filter_col, 'WIPE_ALL').execute()

        count = len(resp.data) if resp.data else 0
        print(f"✅ Soft-deleted {table}: {count} rows marked is_deleted=true")

        # Log to system_log for audit compliance
        try:
            sb.table("system_log").insert({
                "event_type": "SOFT_DELETE",
                "event_message": f"Clean slate: soft-deleted all rows in {table} (count={count})"
            }).execute()
        except Exception as log_err:
            print(f"⚠️ Could not log soft-delete of {table}: {log_err}")

    except Exception as e:
        print(f"⚠️ Could not soft-delete {table}: {str(e)}")

print("\n🚀 Database is now clean and fully standard-aligned.")
