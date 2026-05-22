#!/usr/bin/env python3
"""
CR-20260522: Apply v9.7.2 migration to Supabase.
Adds is_deleted columns to lookup tables for soft-delete compliance.
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="/a0/usr/workdir/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")

PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

MIGRATION_FILE = "/a0/usr/workdir/supabase_db/migrations/v9_7_2_LOOKUP_SOFT_DELETE.sql"


def execute_sql(sql):
    """Execute SQL via Supabase Management API."""
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": sql}
    print(f"SQL length: {len(sql)} chars")
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=120)
        if resp.status_code in (200, 201):
            print(f"SUCCESS (HTTP {resp.status_code})")
            print(f"Response: {resp.text[:300]}")
            return True
        else:
            print(f"FAILED (HTTP {resp.status_code})")
            print(f"Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False


def verify_columns():
    """Verify is_deleted columns exist on lookup tables."""
    sql = """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema='public' 
    AND table_name IN ('species', 'development_stage', 'biological_property')
    AND column_name = 'is_deleted'
    """
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(api_url, headers=headers, json={"query": sql}, timeout=60)
        if resp.status_code in (200, 201):
            data = resp.json()
            print(f"\nVerification results: {data}")
            return len(data) == 3
        else:
            print(f"Verification failed: HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"Verification error: {e}")
        return False


def main():
    print("="*60)
    print("Apply v9.7.2 Migration: LOOKUP_SOFT_DELETE")
    print(f"Project: {PROJECT_REF}")
    print("="*60)

    if not MGMT_TOKEN:
        print("No SUPABASE_MANAGEMENT_API_TOKEN. Cannot proceed.")
        sys.exit(1)

    # Read SQL
    with open(MIGRATION_FILE, "r") as f:
        sql = f.read().strip()

    print(f"\nRead migration file: {len(sql)} chars")

    # Execute
    success = execute_sql(sql)

    if success:
        columns_ok = verify_columns()
        if columns_ok:
            print("\nALL MIGRATIONS APPLIED AND VERIFIED")
        else:
            print("\nMIGRATION APPLIED BUT VERIFICATION INCOMPLETE")
    else:
        print("\nMIGRATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
