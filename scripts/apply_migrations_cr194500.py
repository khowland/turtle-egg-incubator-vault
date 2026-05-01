#!/usr/bin/env python3
"""
CR-20260430-194500: Apply database migrations for Phase 1.2a and 1.3.
Migrations:
  - v8_3_2: Rename ambient_temp → incubator_temp_f on bin_observation
  - v8_3_3: Add observer_id column to system_log
"""
import os
import sys
import urllib.parse
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_URL or not DB_PASSWORD:
    print("❌ Missing SUPABASE_URL or SUPABASE_DB_PASSWORD in .env")
    sys.exit(1)

# Extract project ref from https://ref.supabase.co
project_ref = SUPABASE_URL.split("://")[1].split(".")[0]
DB_HOST = f"db.{project_ref}.supabase.co"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
# Password contains special characters; URL-encode for connection string
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)

CONN_STRING = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"

# SQL file paths
MIGRATION_DIR = "/a0/usr/workdir/supabase_db/migrations"
MIGRATIONS = [
    ("v8_3_2", "v8_3_2_CONSOLIDATE_BIN_OBS_TEMP.sql"),
    ("v8_3_3", "v8_3_3_ADD_OBSERVER_ID_TO_SYSTEM_LOG.sql"),
]

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def read_sql(filename):
    filepath = os.path.join(MIGRATION_DIR, filename)
    if not os.path.exists(filepath):
        print(f"❌ Migration file not found: {filepath}")
        sys.exit(1)
    with open(filepath, "r") as f:
        content = f.read()
    return content

def execute_sql(conn, name, sql_stmt):
    """Execute a SQL statement; handle errors gracefully."""
    print(f"\n{'='*60}")
    print(f"⚙️  Executing {name}...")
    print(f"{'='*60}")
    try:
        with conn.cursor() as cur:
            cur.execute(sql_stmt)
            conn.commit()
            print(f"✅ {name} executed successfully.")
            return True
    except Exception as e:
        conn.rollback()
        print(f"❌ {name} failed: {e}")
        return False

def verify_column(conn, table, column):
    """Check if a column exists in a table."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                  AND column_name = %s
            )
        """, (table, column))
        exists = cur.fetchone()[0]
        return exists

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"🔌 Connecting to database at {DB_HOST}...")
    try:
        conn = psycopg2.connect(CONN_STRING)
        print("✅ Connected successfully.")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)

    # 1. Pre-check: what columns currently exist?
    print("\n📋 Pre-migration column check:")
    has_ambient = verify_column(conn, "bin_observation", "ambient_temp")
    has_incubator_f = verify_column(conn, "bin_observation", "incubator_temp_f")
    has_observer_id = verify_column(conn, "system_log", "observer_id")
    print(f"  bin_observation.ambient_temp present? {has_ambient}")
    print(f"  bin_observation.incubator_temp_f present? {has_incubator_f}")
    print(f"  system_log.observer_id present? {has_observer_id}")

    # 2. Execute Migration 1: Rename column
    if has_ambient and not has_incubator_f:
        sql_rename = read_sql(MIGRATIONS[0][1])
        if not execute_sql(conn, MIGRATIONS[0][0], sql_rename):
            print("⚠️  Rename migration failed. Check manually.")
    elif has_incubator_f:
        print("ℹ️  incubator_temp_f already exists; skipping rename.")
    else:
        print("⚠️  ambient_temp doesn't exist and incubator_temp_f doesn't exist. Nothing to rename.")

    # 3. Execute Migration 2: Add column and FK
    if not has_observer_id:
        sql_add_col = read_sql(MIGRATIONS[1][1])
        if not execute_sql(conn, MIGRATIONS[1][0], sql_add_col):
            print("⚠️  Add column migration failed. Check manually.")
    else:
        print("ℹ️  observer_id already exists in system_log; skipping add.")

    # 4. Post-migration verification
    print("\n📋 Post-migration column check:")
    has_ambient_after = verify_column(conn, "bin_observation", "ambient_temp")
    has_incubator_f_after = verify_column(conn, "bin_observation", "incubator_temp_f")
    has_observer_id_after = verify_column(conn, "system_log", "observer_id")
    print(f"  bin_observation.ambient_temp present? {has_ambient_after}")
    print(f"  bin_observation.incubator_temp_f present? {has_incubator_f_after}")
    print(f"  system_log.observer_id present? {has_observer_id_after}")

    # 5. Full column listing for relevant tables
    print("\n📊 Complete column listing:")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name IN ('bin_observation', 'system_log')
            ORDER BY table_name, ordinal_position
        """)
        rows = cur.fetchall()
        current_table = None
        for col_name, data_type, is_nullable in rows:
            if col_name != current_table:
                current_table = col_name
                print(f"\n  Table: {col_name}")
            print(f"    {col_name}: {data_type} (nullable={is_nullable})")

    conn.close()

    # 6. Final verdict
    if not has_ambient_after and has_incubator_f_after and has_observer_id_after:
        print("\n✅ All migrations applied and verified successfully!")
    else:
        print("\n⚠️  Some verifications failed; review output above.")

if __name__ == "__main__":
    main()
