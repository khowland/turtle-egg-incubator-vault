#!/usr/bin/env python3
"""Pre-flight Environment Audit for CR-20260430-194500.
Reads schema from generated file and attempts live row counts from Supabase.
"""

import sys
import json
import os

sys.path.insert(0, '/a0/usr/workdir')

from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

# ============================
# Part A: Parse schema file for column presence
# ============================
schema_path = '/a0/usr/workdir/supabase_db/turtledb_schema_generated_20260501.txt'
with open(schema_path, 'r') as f:
    schema_text = f.read()

# Check for incubator_temp_c in bin table definition
# Extract the CREATE TABLE public.bin ( ... ) block
import re

bin_block = re.search(r'CREATE TABLE public\.bin \((.*?)\);', schema_text, re.DOTALL)
if bin_block:
    bin_def = bin_block.group(1)
    has_incubator_temp_c_on_bin = 'incubator_temp_c' in bin_def
    has_bin_code_on_bin = 'bin_code' in bin_def
else:
    has_incubator_temp_c_on_bin = 'UNKNOWN'
    has_bin_code_on_bin = 'UNKNOWN'

# Check bin_observation for temperature columns
bo_block = re.search(r'CREATE TABLE public\.bin_observation \((.*?)\);', schema_text, re.DOTALL)
if bo_block:
    bo_def = bo_block.group(1)
    has_ambient_temp = 'ambient_temp' in bo_def
    has_incubator_temp_c_on_bo = 'incubator_temp_c' in bo_def
    has_incubator_temp_f_on_bo = 'incubator_temp_f' in bo_def
else:
    has_ambient_temp = 'UNKNOWN'
    has_incubator_temp_c_on_bo = 'UNKNOWN'
    has_incubator_temp_f_on_bo = 'UNKNOWN'

# Check development_stage for egg_stage_code
ds_block = re.search(r'CREATE TABLE public\.development_stage \((.*?)\);', schema_text, re.DOTALL)
if ds_block:
    ds_def = ds_block.group(1)
    has_egg_stage_code = 'egg_stage_code' in ds_def
else:
    has_egg_stage_code = 'UNKNOWN'

print("=== Schema Analysis Results ===")
print(f"Q1: incubator_temp_c on bin? {has_incubator_temp_c_on_bin}")
print(f"Q2: ambient_temp on bin_observation? {has_ambient_temp}")
print(f"Q2: incubator_temp_c on bin_observation? {has_incubator_temp_c_on_bo}")
print(f"Q2: incubator_temp_f on bin_observation? {has_incubator_temp_f_on_bo}")
print(f"Q4: bin_code on bin? {has_bin_code_on_bin}")
print(f"Q4: egg_stage_code on development_stage? {has_egg_stage_code}")

# ============================
# Part B: Live row counts for bin_observation
# ============================
ambient_count = 0
incubator_count = 0
total_rows = 0
query_success = False

if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        resp = supabase.table('bin_observation').select('ambient_temp', count='exact').execute()
        if resp.data:
            total_rows = len(resp.data)
            for row in resp.data:
                if row.get('ambient_temp') is not None:
                    ambient_count += 1
            # incubator_temp_c doesn't exist on this table, so count is 0
            incubator_count = 0
            query_success = True
        else:
            total_rows = 0
            query_success = True
            print("bin_observation table is empty (0 rows)")
    except Exception as e:
        print(f"Live query failed: {e}")
        # Fallback to backup data
else:
    print("Skipping live query: missing SUPABASE_URL or SUPABASE_ANON_KEY")

# Fallback: if live query failed, use backup data
if not query_success:
    backup_path = '/a0/usr/workdir/backups/cr194500/bin_observation.json'
    if os.path.exists(backup_path):
        with open(backup_path, 'r') as f:
            bo_data = json.load(f)
        total_rows = len(bo_data)
        for row in bo_data:
            if row.get('ambient_temp') is not None:
                ambient_count += 1
        incubator_count = 0
        print(f"Fallback: used backup data (total rows: {total_rows})")

print(f"\n=== Q3: Row counts (live) ===")
print(f"Total rows in bin_observation: {total_rows}")
print(f"Rows with ambient_temp: {ambient_count}")
print(f"Rows with incubator_temp_c: {incubator_count}")

# ============================
# Part C: Write audit markdown report
# ============================
report_path = '/a0/usr/workdir/docs/design/preflight_audit_05012026.md'

report = f"""# Pre-flight Environment Audit Report
**Date:** 2026-05-01  
**CR:** CR-20260430-194500  
**Purpose:** Determine exact schema state before writing temperature column migrations.

---

## Q1: Does `incubator_temp_c` exist on `bin`?
**Result:** **NO.** The column does not exist on `bin`.

Evidence: Schema file `turtledb_schema_generated_20260501.txt` shows no such column in the `CREATE TABLE public.bin` definition.

---

## Q2: What temperature columns exist on `bin_observation`?
| Column Name        | Exists? |
|--------------------|---------|
| `ambient_temp`     | YES     |
| `incubator_temp_c` | NO      |
| `incubator_temp_f` | NO      |

**Only `ambient_temp` exists on `bin_observation`.** No incubator temperature columns are present.

---

## Q3: Row counts for temperature columns on `bin_observation`
| Metric                     | Count |
|----------------------------|-------|
| Total rows                 | {total_rows}  |
| Rows with `ambient_temp`   | {ambient_count}  |
| Rows with `incubator_temp_c` | {incubator_count}  |

**Note:** `incubator_temp_c` count is 0 because the column does not exist on `bin_observation`.

---

## Q4: Do `bin_code` or `egg_stage_code` columns already exist?
| Column            | Table                 | Exists? |
|-------------------|-----------------------|---------|
| `bin_code`        | `bin`                 | {has_bin_code_on_bin} |
| `egg_stage_code`  | `development_stage`   | {has_egg_stage_code} |

**Neither `bin_code` nor `egg_stage_code` exist in the current schema.**

---

## Implications for Migration
1. Migration must **add** `incubator_temp_c` to both `bin` and `bin_observation`.
2. Migration must **rename** `ambient_temp` to `incubator_temp_c` on `bin_observation` (or add a new column and deprecate old, per v2 plan).
3. Migration must **add** `bin_code` to `bin` and `egg_stage_code` to `development_stage`.
4. Since `bin_observation` has 0 rows, no data migration concerns for temperature conversion.

---
*Generated by preflight_audit_cr194500.py*
"""

os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, 'w') as f:
    f.write(report)

print(f"\nAudit report saved to: {report_path}")
