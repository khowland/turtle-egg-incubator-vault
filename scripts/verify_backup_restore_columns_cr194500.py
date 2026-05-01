#!/usr/bin/env python3
"""
CR-20260430-194500: Verify backup/restore RPCs use incubator_temp_f (not incubator_temp_c or ambient_temp).
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="/a0/usr/workdir/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]
API_URL = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
HEADERS = {"Authorization": f"Bearer {MGMT_TOKEN}", "Content-Type": "application/json"}

def exec_sql(label, sql):
    r = requests.post(API_URL, headers=HEADERS, json={"query": sql}, timeout=30)
    ok = r.status_code in (200, 201)
    tag = "OK" if ok else "FAIL"
    print(f"  [{label}]: {tag} ({r.status_code})")
    if not ok:
        print(f"    {r.text[:200]}")
    return ok, r.text

def main():
    print("=" * 60)
    print("CR-20260430-194500: Backup/Restore Column Verification")
    print("=" * 60)

    all_pass = True

    # 1. Verify bin_observation columns in DB
    print("\n[1] Checking bin_observation columns in DB...")
    sql1 = (
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'bin_observation' AND table_schema = 'public' "
        "AND column_name IN ('incubator_temp_f', 'incubator_temp_c', 'ambient_temp') "
        "ORDER BY column_name;"
    )
    ok, result = exec_sql("bin_observation columns", sql1)
    if ok:
        if "incubator_temp_f" in result and "incubator_temp_c" not in result and "ambient_temp" not in result:
            print("    [PASS] Only incubator_temp_f found; no old column references.")
        else:
            print(f"    [FAIL] Unexpected columns: {result.strip()}")
            all_pass = False
    else:
        all_pass = False

    # 2. Check vault_admin_restore RPC source
    print("\n[2] Checking vault_admin_restore RPC source...")
    sql2 = (
        "SELECT prosrc FROM pg_proc "
        "WHERE proname = 'vault_admin_restore' "
        "AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');"
    )
    ok, result = exec_sql("vault_admin_restore source", sql2)
    if ok:
        if "incubator_temp_c" in result or "ambient_temp" in result:
            print("    [FAIL] OLD column references found in vault_admin_restore RPC!")
            all_pass = False
        elif "incubator_temp_f" in result:
            print("    [PASS] vault_admin_restore uses incubator_temp_f correctly.")
        else:
            print("    [INFO] No temperature references found (may be truncated).")
    else:
        all_pass = False

    # 3. Check vault_export_full_backup RPC source
    print("\n[3] Checking vault_export_full_backup RPC source...")
    sql3 = (
        "SELECT prosrc FROM pg_proc "
        "WHERE proname = 'vault_export_full_backup' "
        "AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');"
    )
    ok, result = exec_sql("vault_export_full_backup source", sql3)
    if ok:
        if "incubator_temp_c" in result or "ambient_temp" in result:
            print("    [FAIL] OLD column references found!")
            all_pass = False
        else:
            print("    [PASS] No old temperature column references.")
    else:
        all_pass = False

    # 4. Check vault_restore_from_backup RPC source
    print("\n[4] Checking vault_restore_from_backup RPC source...")
    sql4 = (
        "SELECT prosrc FROM pg_proc "
        "WHERE proname = 'vault_restore_from_backup' "
        "AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');"
    )
    ok, result = exec_sql("vault_restore_from_backup source", sql4)
    if ok:
        if "incubator_temp_c" in result or "ambient_temp" in result:
            print("    [FAIL] OLD column references found!")
            all_pass = False
        else:
            print("    [PASS] No old temperature column references.")
    else:
        all_pass = False

    # 5. Check 5_Settings.py file for old references
    print("\n[5] Checking 5_Settings.py for old column references...")
    try:
        with open("/a0/usr/workdir/vault_views/5_Settings.py", "r") as f:
            content = f.read()
        if "incubator_temp_c" in content or "ambient_temp" in content:
            print("    [FAIL] OLD column references found in 5_Settings.py!")
            all_pass = False
        else:
            print("    [PASS] No old column references in 5_Settings.py.")
    except Exception as e:
        print(f"    [FAIL] Could not read file: {e}")
        all_pass = False

    # Summary
    print("\n" + "=" * 60)
    if all_pass:
        print("[PASS] All backup/restore column alignment checks passed.")
    else:
        print("[FAIL] One or more checks failed.")
    print("=" * 60)
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
