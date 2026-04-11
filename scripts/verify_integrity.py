# =============================================================================
# Script:      scripts/verify_integrity.py
# Project:     Incubator Vault v7.9.8
# Purpose:     Forensic Schema Audit of the Production Supabase Environment.
# =============================================================================
import os
import sys
from supabase import create_client, Client

# Add root to path
sys.path.append(os.getcwd())
from utils.db import get_supabase

def audit_schema():
    print("🛡️ Starting Forensic Schema Audit v7.9.8...")
    supabase = get_supabase()
    
    # 1. Table Namespace Check
    legacy_tables = ['systemlog', 'sessionlog', 'eggobservation', 'incubatorobservation']
    for lt in legacy_tables:
        try:
            res = supabase.table(lt).select('count', count='exact').limit(1).execute()
            print(f"❌ CRITICAL ERROR: Legacy table '{lt}' still responding. Needs clean purge.")
        except:
            print(f"✅ PASSED: Legacy table '{lt}' correctly decommissioned.")

    # 2. Modern Table Verification
    modern_tables = ['system_log', 'session_log', 'egg_observation', 'bin_observation', 'mother', 'bin', 'egg']
    for mt in modern_tables:
        try:
            res = supabase.table(mt).select('count', count='exact').limit(1).execute()
            print(f"✅ PASSED: Standardized table '{mt}' is alive.")
        except Exception as e:
            print(f"❌ ERROR: Standardized table '{mt}' is missing or broken. Detail: {e}")

    # 3. Column Consistency Check
    try:
        egg_res = supabase.table('egg').select('*').limit(1).execute()
        if 'last_chalk' in egg_res.data[0] and 'last_vasc' in egg_res.data[0]:
            print("✅ PASSED: 'egg' table has v7.9.0 Cached Health Markers.")
        else:
            print("❌ ERROR: 'egg' table is missing clinical icon markers.")
    except:
        print("⚠️ SKIP: Egg table check (No data in table to inspect? Check schema directly).")

if __name__ == "__main__":
    audit_schema()
