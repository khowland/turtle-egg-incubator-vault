#!/usr/bin/env python3
"""
CR-20260430-194500: Phase 6 — Add bin_code and egg_stage_code columns.
Executes ALTER TABLE + UPDATE for both columns, then verifies.
Methods:
  1) psycopg2 with resolved IPv4 address (direct)
  2) Supabase Management API SQL endpoint (fallback)
"""
import os
import sys
import socket
import urllib.parse
import requests
import psycopg2

# ---------------------------------------------------------------------------
# Load .env explicitly by path
# ---------------------------------------------------------------------------
from dotenv import load_dotenv
load_dotenv(dotenv_path="/a0/usr/workdir/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")

PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]
DB_HOST = f"db.{PROJECT_REF}.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"

# SQL statements to execute (ALTER + UPDATE combined per table)
MIGRATION_SQLS = [
    ("v8_4_1: Add bin_code to bin", """
ALTER TABLE public.bin ADD COLUMN IF NOT EXISTS bin_code text;
UPDATE public.bin SET bin_code = bin_id WHERE bin_code IS NULL;
""".strip()),
    ("v8_4_2: Add egg_stage_code to development_stage", """
ALTER TABLE public.development_stage ADD COLUMN IF NOT EXISTS egg_stage_code text;
UPDATE public.development_stage SET egg_stage_code = stage_id WHERE egg_stage_code IS NULL;
""".strip()),
]

# Verification queries
VERIFY_SQLS = [
    ("Check bin.bin_code exists and matches bin_id", """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'bin'
  AND column_name = 'bin_code';
""".strip()),
    ("Check bin.bin_code values match bin_id", """
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE bin_code IS NOT NULL AND bin_code = bin_id) AS matching,
       COUNT(*) FILTER (WHERE bin_code IS NOT NULL AND bin_code <> bin_id) AS mismatched,
       COUNT(*) FILTER (WHERE bin_code IS NULL) AS nulls
FROM public.bin;
""".strip()),
    ("Check development_stage.egg_stage_code exists", """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'development_stage'
  AND column_name = 'egg_stage_code';
""".strip()),
    ("Check development_stage.egg_stage_code values match stage_id", """
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE egg_stage_code IS NOT NULL AND egg_stage_code = stage_id) AS matching,
       COUNT(*) FILTER (WHERE egg_stage_code IS NOT NULL AND egg_stage_code <> stage_id) AS mismatched,
       COUNT(*) FILTER (WHERE egg_stage_code IS NULL) AS nulls
FROM public.development_stage;
""".strip()),
]


def resolve_ipv4(host):
    """Resolve hostname to IPv4 address."""
    try:
        info = socket.getaddrinfo(host, 5432, socket.AF_INET, socket.SOCK_STREAM)
        return info[0][4][0]
    except Exception as e:
        print(f"❌ IPv4 resolution failed: {e}")
        return None


def try_psycopg2(ipv4_address):
    """Attempt migration via psycopg2 with IPv4 hostaddr."""
    encoded_pw = urllib.parse.quote_plus(DB_PASSWORD)
    conn_str = f"postgresql://{DB_USER}:{encoded_pw}@{ipv4_address}:{DB_PORT}/{DB_NAME}?sslmode=require"
    print(f"🔌 Connecting via psycopg2 to {ipv4_address}...")
    try:
        conn = psycopg2.connect(conn_str)
        print("✅ Connected via psycopg2.")
        return conn
    except Exception as e:
        print(f"❌ psycopg2 failed: {e}")
        return None


def execute_via_mgmt_api(name, sql):
    """Execute SQL via Supabase Management API."""
    if not MGMT_TOKEN:
        print("❌ No management API token available.")
        return False
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    all_ok = True
    for stmt in statements:
        payload = {"query": stmt + ";"}
        try:
            resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
            if resp.status_code in (200, 201):
                print(f"  ✅ Executed: {stmt[:60]}... Status={resp.status_code}")
            else:
                print(f"  ❌ Failed ({resp.status_code}): {stmt[:60]}... -> {resp.text[:300]}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_ok = False
    return all_ok


def verify_via_mgmt_api(name, sql):
    """Run a verification query via Management API."""
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": sql}
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"  Verification '{name}': HTTP {resp.status_code}")
        if resp.status_code in (200, 201):
            print(f"  Result: {resp.text[:500]}")
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("CR-20260430-194500: Phase 6 — PK Column Addition")
    print("=" * 60)
    print(f"Project Ref: {PROJECT_REF}")

    conn = None
    use_api = False

    # --- Method 1: psycopg2 with IPv4 ---
    print("\n🔍 Resolving IPv4 for database host...")
    ipv4 = resolve_ipv4(DB_HOST)
    if ipv4:
        print(f"  IPv4: {ipv4}")
        conn = try_psycopg2(ipv4)
    else:
        print("  No IPv4 address resolved.")

    # --- Method 2: Management API fallback ---
    if not conn:
        print("\n🔄 Falling back to Supabase Management API...")
        if not MGMT_TOKEN:
            print("❌ No SUPABASE_MANAGEMENT_API_TOKEN in .env. Cannot proceed.")
            sys.exit(1)
        # Test connectivity
        print("  Testing API connectivity...")
        test_ok = verify_via_mgmt_api("connectivity test", "SELECT 1 AS test;")
        if not test_ok:
            print("❌ Management API unreachable. Manual execution required.")
            sys.exit(1)
        use_api = True

    # --- Execute Migrations ---
    print("\n⚙️  Executing migrations...")
    for mig_name, sql in MIGRATION_SQLS:
        print(f"\n  Running: {mig_name}")
        if use_api:
            ok = execute_via_mgmt_api(mig_name, sql)
            if not ok:
                print(f"  ⚠ Warning: Some statements for {mig_name} may have failed.")
        else:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    conn.commit()
                    print(f"  ✅ {mig_name} executed via psycopg2.")
            except Exception as e:
                conn.rollback()
                print(f"  ❌ {mig_name} failed: {e}")

    # --- Post-migration Verification ---
    print("\n📋 Post-migration verification...")
    if use_api:
        for name, sql in VERIFY_SQLS:
            verify_via_mgmt_api(name, sql)
    else:
        with conn.cursor() as cur:
            for name, sql in VERIFY_SQLS:
                cur.execute(sql)
                rows = cur.fetchall()
                print(f"  {name}: {rows}")

    if conn:
        conn.close()

    print("\n✅ Phase 6 script complete.")


if __name__ == "__main__":
    main()
