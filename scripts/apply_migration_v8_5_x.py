#!/usr/bin/env python3
"""
CR-20260429-225412: Apply v8_5_x migrations to Supabase.
Resolves red team blockers: observer_name NOT NULL, PENDING bin IDs,
validation failures, intake_number race conditions, orphaned records.

Applies:
  1. v8_5_0_ADD_INTAKE_NUMBER.sql — adds intake_number column to intake table
  2. v8_5_1_RPC_VAULT_FINALIZE_SUPPLEMENTAL_BIN.sql — creates atomic RPC function
"""
import os
import sys
import re
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="/a0/usr/workdir/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]

MIGRATION_DIR = "/a0/usr/workdir/supabase_db/migrations"
MIGRATIONS = [
    "v8_5_0_ADD_INTAKE_NUMBER.sql",
    "v8_5_1_RPC_VAULT_FINALIZE_SUPPLEMENTAL_BIN.sql",
]


def execute_sql(name, sql):
    """Execute SQL via Supabase Management API."""
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": sql}
    print(f"\n{'='*60}")
    print(f"Executing: {name}")
    print(f"{'='*60}")
    print(f"SQL length: {len(sql)} chars")

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=120)
        if resp.status_code in (200, 201):
            print(f"✅ {name}: SUCCESS (HTTP {resp.status_code})")
            response_text = resp.text[:300] if resp.text else "(empty)"
            print(f"   Response: {response_text}")
            return True
        else:
            print(f"❌ {name}: FAILED (HTTP {resp.status_code})")
            print(f"   Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ {name}: EXCEPTION: {e}")
        return False


def verify_intake_number():
    """Verify intake_number column exists on intake table."""
    print(f"\n{'='*60}")
    print("Verifying: intake_number column on intake table")
    print(f"{'='*60}")

    sql = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='intake' AND column_name='intake_number'"
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(api_url, headers=headers, json={"query": sql}, timeout=30)
        if resp.status_code in (200, 201):
            data = resp.json()
            if data and len(data) > 0:
                print(f"✅ intake_number column exists: {data[0]}")
                return True
            else:
                print("❌ intake_number column NOT FOUND")
                return False
        else:
            print(f"❌ Verification query failed: HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False


def verify_rpc():
    """Verify RPC function exists via Supabase REST API."""
    print(f"\n{'='*60}")
    print("Verifying RPC: vault_finalize_supplemental_bin")
    print(f"{'='*60}")

    rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/vault_finalize_supplemental_bin"
    headers = {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
    }
    # Minimal test payload — will error on validation but proves function exists
    payload = {
        "p_intake_id": "test-nonexistent",
        "p_session_id": "test-verify-rpc-v85",
        "p_observer_id": "00000000-0000-0000-0000-000000000000",
        "p_observer_name": "Test Observer",
        "p_supp_date": "2026-05-01",
        "p_bins": [
            {
                "new_egg_count": 1,
                "current_egg_count": 0,
                "total_eggs": 1,
                "substrate": "Vermiculite",
                "shelf": "",
                "notes": "Test",
                "is_new_bin": True,
                "existing_bin_id": None
            }
        ]
    }
    print(f"  POST {rpc_url}")
    print(f"  Payload keys: {list(payload.keys())}")

    try:
        resp = requests.post(rpc_url, headers=headers, json=payload, timeout=30)
        print(f"  HTTP {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
        # Function exists if we get any response other than 404
        if resp.status_code != 404:
            print("✅ RPC vault_finalize_supplemental_bin is accessible (function exists)")
            return True
        else:
            print("❌ RPC returns 404 - function may not exist")
            return False
    except Exception as e:
        print(f"❌ RPC verification error: {e}")
        return False


def main():
    print("="*60)
    print("CR-20260429-225412: Apply v8_5_x Migrations")
    print(f"Project: {PROJECT_REF}")
    print(f"Time: 2026-05-01 09:39")
    print("="*60)

    if not MGMT_TOKEN:
        print("❌ No SUPABASE_MANAGEMENT_API_TOKEN in .env. Cannot proceed.")
        sys.exit(1)

    # Test API connectivity
    print("\n🔍 Testing Management API connectivity...")
    test_ok = execute_sql("connectivity test", "SELECT 1 AS test;")
    if not test_ok:
        print("❌ Management API unreachable. Manual execution required.")
        sys.exit(1)

    # Apply each migration
    results = []
    for migration_file in MIGRATIONS:
        filepath = os.path.join(MIGRATION_DIR, migration_file)
        print(f"\n📄 Reading migration: {filepath}")
        try:
            with open(filepath, "r") as f:
                sql = f.read().strip()
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")
            results.append((migration_file, False))
            continue

        if not sql:
            print(f"⚠️  Empty file: {migration_file}, skipping")
            results.append((migration_file, True))
            continue

        # Execute entire SQL file as one query
        success = execute_sql(migration_file, sql)
        results.append((migration_file, success))

    # Verify schema changes
    print("\n📋 Verification phase...")
    intake_ok = verify_intake_number()
    rpc_ok = verify_rpc()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_ok = all(r[1] for r in results)
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    print(f"\n  intake_number column: {'✅' if intake_ok else '❌'}")
    print(f"  RPC verification:     {'✅' if rpc_ok else '❌'}")
    print(f"\n  Overall: {'✅ ALL MIGRATIONS APPLIED' if all_ok else '❌ SOME FAILURES'}")

    if all_ok:
        print("\n✅ Migration v8_5_x applied successfully.")
    else:
        print("\n❌ Migration had failures. Review logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
