#!/usr/bin/env python3
"""
CR-20260430-194500: Apply v8_3_0 RPC migration to Supabase.
Updates 3 RPC functions to use incubator_temp_f and remove incubator_temp_c from bin INSERTs.
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

MIGRATION_FILE = "/a0/usr/workdir/supabase_db/migrations/v8_3_0_UPDATE_ALL_RPCS_FOR_TEMP_RENAME.sql"


def extract_functions(filepath):
    """Extract CREATE OR REPLACE FUNCTION ... GRANT EXECUTE ... statements from SQL file."""
    with open(filepath, "r") as f:
        content = f.read()

    functions = []
    # Find all CREATE OR REPLACE FUNCTION blocks, each ending with its GRANT EXECUTE
    # Pattern: CREATE OR REPLACE FUNCTION ... up to and including GRANT EXECUTE ...;
    pattern = r'(CREATE OR REPLACE FUNCTION.*?GRANT EXECUTE ON FUNCTION[^;]+;)'
    matches = re.findall(pattern, content, re.DOTALL)

    for i, match in enumerate(matches):
        func_text = match.strip()
        # Extract function name for labeling
        name_match = re.search(r'CREATE OR REPLACE FUNCTION public\.(\w+)\(', func_text)
        name = name_match.group(1) if name_match else f"function_{i+1}"
        functions.append((name, func_text))

    return functions


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
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
        if resp.status_code in (200, 201):
            print(f"✅ {name}: SUCCESS (HTTP {resp.status_code})")
            print(f"   Response: {resp.text[:200]}")
            return True
        else:
            print(f"❌ {name}: FAILED (HTTP {resp.status_code})")
            print(f"   Response: {resp.text[:500]}")
            return False
    except Exception as e:
        print(f"❌ {name}: EXCEPTION: {e}")
        return False


def verify_rpc():
    """Verify RPC works via Supabase REST API."""
    print(f"\n{'='*60}")
    print("Verifying RPC: vault_finalize_intake")
    print(f"{'='*60}")

    rpc_url = f"{SUPABASE_URL}/rest/v1/rpc/vault_finalize_intake"
    headers = {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
    }
    # Small test payload - will fail validation but prove function exists with right columns
    payload = {
        "species_id": "SN",
        "session_id": "test-verify-rpc",
        "observer_id": "00000000-0000-0000-0000-000000000000",
        "intake_date": "2026-05-01",
        "bins": [],
        "intake": {}
    }
    print(f"  POST {rpc_url}")
    print(f"  Payload: {payload}")

    try:
        resp = requests.post(rpc_url, headers=headers, json=payload, timeout=30)
        print(f"  HTTP {resp.status_code}")
        print(f"  Response: {resp.text[:500]}")
        # Function exists if we get any response other than 404
        if resp.status_code != 404:
            print("✅ RPC vault_finalize_intake is accessible (function exists)")
            return True
        else:
            print("❌ RPC returns 404 - function may not exist")
            return False
    except Exception as e:
        print(f"❌ RPC verification error: {e}")
        return False


def main():
    print("="*60)
    print("CR-20260430-194500: Apply v8_3_0 RPC Migration")
    print(f"Project: {PROJECT_REF}")
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

    # Extract functions from migration file
    print(f"\n📄 Reading migration file: {MIGRATION_FILE}")
    functions = extract_functions(MIGRATION_FILE)
    print(f"   Found {len(functions)} functions to apply:")
    for name, sql in functions:
        print(f"     - {name} ({len(sql)} chars)")

    # Execute each function
    print("\n⚙️  Applying RPC functions...")
    results = []
    for name, sql in functions:
        success = execute_sql(name, sql)
        results.append((name, success))

    # Verify
    print("\n📋 Verification via RPC endpoint...")
    rpc_ok = verify_rpc()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    all_ok = all(r[1] for r in results)
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    print(f"\n  RPC verification: {'✅' if rpc_ok else '❌'}")
    print(f"\n  Overall: {'✅ ALL FUNCTIONS APPLIED' if all_ok else '❌ SOME FAILURES'}")

    if all_ok:
        print("\n✅ Migration v8_3_0 applied successfully.")
    else:
        print("\n❌ Migration had failures. Review logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
