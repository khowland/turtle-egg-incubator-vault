#!/usr/bin/env python3
"""
Backup script for CR-20260430-194500.
Exports all public tables from Supabase (turtle-db) to JSON files.
Uses Supabase Python client (REST API) to fetch data.
Tables list extracted from project schema.
"""
import sys
sys.path.insert(0, '/a0/usr/workdir')
import os
import json
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

def main():
    url = os.getenv('SUPABASE_URL')
    anon_key = os.getenv('SUPABASE_ANON_KEY')
    if not url or not anon_key:
        print("ERROR: SUPABASE_URL or SUPABASE_ANON_KEY missing")
        sys.exit(1)
    supabase = create_client(url, anon_key)

    # All known public tables (from schema export 04282026)
    tables = [
        'bin',
        'bin_observation',
        'biological_property',
        'development_stage',
        'egg',
        'egg_observation',
        'hatchling_ledger',
        'intake',
        'observer',
        'session_log',
        'species',
        'system_config',
        'system_log'
    ]

    backup_dir = '/a0/usr/workdir/backups/cr194500'
    os.makedirs(backup_dir, exist_ok=True)

    total_rows = 0
    success = True
    for table in tables:
        try:
            response = supabase.table(table).select('*').execute()
            data = response.data
            filepath = os.path.join(backup_dir, f"{table}.json")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            rows = len(data)
            total_rows += rows
            print(f"  ✓ {table}: {rows} rows -> {filepath}")
        except Exception as e:
            print(f"  ✗ {table}: error - {e}")
            success = False

    print(f"Backup complete. Total rows: {total_rows}")
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
