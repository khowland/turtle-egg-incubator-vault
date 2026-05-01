#!/usr/bin/env python3
"""
CR-20260430-194500: Apply database migrations (v2 with IPv4 fallback).
Migrations:
  - v8_3_2: Rename ambient_temp → incubator_temp_f on bin_observation
  - v8_3_3: Add observer_id column to system_log

Attempts:
  1) psycopg2 with resolved IPv4 address
  2) Supabase Management API SQL endpoint
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
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
MGMT_TOKEN = os.getenv("SUPABASE_MANAGEMENT_API_TOKEN")

PROJECT_REF = SUPABASE_URL.split("://")[1].split(".")[0]
DB_HOST = f"db.{PROJECT_REF}.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"

MIGRATION_SQLS = [
    ("v8_3_2", "ALTER TABLE public.bin_observation RENAME COLUMN ambient_temp TO incubator_temp_f;"),
    ("v8_3_3", """
ALTER TABLE public.system_log ADD COLUMN IF NOT EXISTS observer_id uuid;
ALTER TABLE public.system_log ADD CONSTRAINT system_log_observer_id_fkey
    FOREIGN KEY (observer_id) REFERENCES public.observer(observer_id);
""".strip()),
]

VERIFY_SQLS = [
    ("bin_observation check", """
SELECT column_name FROM information_schema.columns
WHERE table_name = 'bin_observation' AND column_name IN ('ambient_temp', 'incubator_temp_f')
ORDER BY column_name;
""".strip()),
    ("system_log check", """
SELECT column_name FROM information_schema.columns
WHERE table_name = 'system_log' AND column_name = 'observer_id';
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
    payload = {"query": sql}
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            print(f"✅ Management API: {name} executed. Status={resp.status_code}")
            return True
        else:
            print(f"❌ Management API: {name} failed ({resp.status_code}): {resp.text[:300]}")
            return False
    except Exception as e:
        print(f"❌ Management API error: {e}")
        return False

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
        print(f"  Verification '{name}': {resp.status_code}")
        if resp.status_code in (200, 201):
            print(f"  Result: {resp.text[:200]}")
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print("="*60)
    print("CR-20260430-194500: Database Migration Executor")
    print("="*60)

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
    print("\n📊 Pre-migration verification...")
    if use_api:
        for name, sql in VERIFY_SQLS:
            verify_via_mgmt_api(name, sql)
    else:
        with conn.cursor() as cur:
            for name, sql in VERIFY_SQLS:
                cur.execute(sql)
                print(f"  {name}: {cur.fetchall()}")

    print("\n⚙️  Executing migrations...")
    for mig_name, sql in MIGRATION_SQLS:
        print(f"\n  Running: {mig_name}")
        if use_api:
            execute_via_mgmt_api(mig_name, sql)
        else:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql)
                    conn.commit()
                    print(f"✅ {mig_name} executed via psycopg2.")
            except Exception as e:
                conn.rollback()
                print(f"❌ {mig_name} failed: {e}")

    # --- Verify ---
    print("\n📋 Post-migration verification...")
    if use_api:
        for name, sql in VERIFY_SQLS:
            verify_via_mgmt_api(name, sql)
    else:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name IN ('bin_observation', 'system_log')
                  AND column_name IN ('ambient_temp', 'incubator_temp_f', 'observer_id')
                ORDER BY table_name, ordinal_position;
            """)
            rows = cur.fetchall()
            print(f"  Current state: {rows}")

    if conn:
        conn.close()

    print("\n✅ Migration script complete.")

if __name__ == "__main__":
    main()
