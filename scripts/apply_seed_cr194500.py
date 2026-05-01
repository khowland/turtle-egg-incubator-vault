#!/usr/bin/env python3
"""
CR-20260430-194500: Apply seed lookup tables (species, development_stage, biological_property).
Reads SQL from migration file and executes via psycopg2 (with IPv4) or Supabase Management API.
"""
import os
import sys
import socket
import urllib.parse
import requests
import psycopg2

# ---------------------------------------------------------------------------
# Load .env
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

SEED_SQL_PATH = "/a0/usr/workdir/supabase_db/migrations/v8_3_5_SEED_LOOKUP_TABLES.sql"

VERIFY_SQLS = [
    ("species count", "SELECT count(*) AS cnt FROM public.species;"),
    ("development_stage count", "SELECT count(*) AS cnt FROM public.development_stage;"),
    ("biological_property count", "SELECT count(*) AS cnt FROM public.biological_property;"),
]

def resolve_ipv4(host):
    try:
        info = socket.getaddrinfo(host, 5432, socket.AF_INET, socket.SOCK_STREAM)
        return info[0][4][0]
    except Exception as e:
        print(f"[FAIL] IPv4 resolution failed: {e}")
        return None

def try_psycopg2(ipv4_address):
    encoded_pw = urllib.parse.quote_plus(DB_PASSWORD)
    conn_str = f"postgresql://{DB_USER}:{encoded_pw}@{ipv4_address}:{DB_PORT}/{DB_NAME}?sslmode=require"
    print(f"[CONN] Connecting via psycopg2 to {ipv4_address}...")
    try:
        conn = psycopg2.connect(conn_str)
        print("[OK] Connected via psycopg2.")
        return conn
    except Exception as e:
        print(f"[FAIL] psycopg2 failed: {e}")
        return None

def execute_via_mgmt_api(label, sql):
    if not MGMT_TOKEN:
        print("[FAIL] No management API token.")
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
            print(f"  [OK] {label} executed.")
            return True
        else:
            print(f"  [FAIL] {label} failed ({resp.status_code}): {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def verify_via_mgmt_api(name, sql):
    api_url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    headers = {
        "Authorization": f"Bearer {MGMT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": sql}
    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print(f"  [VERIFY] '{name}': status={resp.status_code}")
        if resp.status_code in (200, 201):
            print(f"  Result: {resp.text.strip()}")
            return True
        else:
            print(f"  [FAIL] Body: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def main():
    print("="*60)
    print("CR-20260430-194500: Seed Lookup Tables")
    print("="*60)

    # Read seed SQL
    with open(SEED_SQL_PATH, 'r') as f:
        seed_sql = f.read()
    print(f"\n[INFO] Read seed SQL: {len(seed_sql)} bytes")

    conn = None
    use_api = False

    # --- Try psycopg2 ---
    print("\n[DNS] Resolving IPv4 for database host...")
    ipv4 = resolve_ipv4(DB_HOST)
    if ipv4:
        print(f"  IPv4: {ipv4}")
        conn = try_psycopg2(ipv4)
    else:
        print("  No IPv4 address resolved.")

    # --- Fallback to Management API ---
    if not conn:
        print("\n[FALLBACK] Trying Supabase Management API...")
        if not MGMT_TOKEN:
            print("[FAIL] No SUPABASE_MANAGEMENT_API_TOKEN in .env. Cannot proceed.")
            sys.exit(1)
        test_ok = verify_via_mgmt_api("connectivity test", "SELECT 1 AS test;")
        if not test_ok:
            print("[FAIL] Management API unreachable.")
            sys.exit(1)
        use_api = True

    # --- Execute Seed SQL ---
    print("\n[EXEC] Running seed SQL...")
    if use_api:
        execute_via_mgmt_api("seed_all", seed_sql)
    else:
        try:
            with conn.cursor() as cur:
                cur.execute(seed_sql)
                conn.commit()
                print("[OK] Seed SQL executed via psycopg2.")
        except Exception as e:
            conn.rollback()
            print(f"[FAIL] Seed SQL failed via psycopg2: {e}")
            print("[FALLBACK] Attempting via Management API instead...")
            execute_via_mgmt_api("seed_all_fallback", seed_sql)

    # --- Verify ---
    print("\n[VERIFY] Post-seed row counts...")
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

    print("\n[DONE] Seed script complete.")

if __name__ == "__main__":
    main()
