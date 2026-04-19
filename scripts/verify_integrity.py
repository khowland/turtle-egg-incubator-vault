# =============================================================================
# Script:      scripts/verify_integrity.py
# Project:     Incubator Vault v7.9.9 — Titan Engine
# Purpose:     Forensic Schema Audit of the Production Supabase Environment.
# =============================================================================
import os
import sys

# Add root to path
sys.path.append(os.getcwd())
from utils.db import get_supabase

def audit_schema():
    print("🛡️ Starting Titan Engine Enterprise Schema Audit v7.9.9...")
    supabase = get_supabase()
    
    # 1. Legacy Table Namespace Check (Should be DECOMMISSIONED)
    legacy_tables = ['systemlog', 'sessionlog', 'eggobservation', 'incubatorobservation']
    for lt in legacy_tables:
        try:
            res = supabase.table(lt).select('count', count='exact').limit(1).execute()
            print(f"❌ CRITICAL ERROR: Legacy table '{lt}' still responding. Transformation failed.")
        except:
            print(f"✅ PASSED: Legacy table '{lt}' correctly transformed/purged.")

    # 2. Modern Enterprise Table Verification (§35)
    modern_tables = ['system_log', 'session_log', 'egg_observation', 'bin_observation', 'mother', 'bin', 'egg', 'hatchling_ledger']
    for mt in modern_tables:
        try:
            res = supabase.table(mt).select('*', count='exact').limit(1).execute()
            print(f"✅ PASSED: Enterprise table '{mt}' is alive.")
            
            # Contextual PK Check
            pk_name = f"{mt}_id" if mt != 'system_log' else 'system_log_id'
            try:
                supabase.table(mt).select(pk_name).limit(1).execute()
                print(f"   - Verified Contextual PK: '{pk_name}'")
            except:
                print(f"   - ⚠️ ALERT: Non-Standard PK on table '{mt}'")
                
            # Clinical Metric Check for bin_observation
            if mt == 'bin_observation':
                for col in ['bin_weight_g', 'water_added_ml', 'env_notes']:
                    try:
                        supabase.table(mt).select(col).limit(1).execute()
                        print(f"   - Verified Clinical Metric: '{col}'")
                    except:
                        print(f"   - ❌ MISSING Clinical Metric: '{col}'")
                        
        except Exception as e:
            print(f"❌ ERROR: Enterprise table '{mt}' is missing or broken. Detail: {e}")

    # 3. Authorship Alignment Check (§35.4)
    print("\n✍️ Checking Authorship Standard (§35.4)...")
    authorship_tables = ['intake', 'bin', 'egg', 'egg_observation', 'bin_observation']
    for at in authorship_tables:
        try:
            res = supabase.table(at).select('created_by_id, modified_by_id').limit(1).execute()
            print(f"✅ PASSED: '{at}' has authorship auditing signatures.")
        except:
            print(f"❌ ERROR: '{at}' violates §35.4 (Authorship columns missing/type mismatch).")

if __name__ == "__main__":
    audit_schema()
