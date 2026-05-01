# CR-20260430-194500: Test vault_admin_restore RPC uses incubator_temp_f in seed data
"""
Test that v8_3_0 migration SQL for vault_admin_restore:
- Contains incubator_temp_f for bin_observation INSERTs
- Does NOT contain incubator_temp_c (except in comments)
- bin INSERT statements do not include incubator_temp_c
"""
import os
import re
import pytest


def _load_migration_sql():
    """Load the v8_3_0 migration SQL file."""
    path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "supabase_db", "migrations",
        "v8_3_0_UPDATE_ALL_RPCS_FOR_TEMP_RENAME.sql"
    )
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_migration_contains_incubator_temp_f():
    """Migration SQL must reference incubator_temp_f."""
    sql = _load_migration_sql()
    assert "incubator_temp_f" in sql, \
        "Migration must reference incubator_temp_f"


def test_migration_no_active_incubator_temp_c():
    """Migration SQL must not contain incubator_temp_c in active SQL code."""
    sql = _load_migration_sql()
    # Strip comments (both -- and /* */ style)
    lines = sql.split("\n")
    active_lines = []
    in_block = False
    for line in lines:
        if "/*" in line:
            in_block = True
        if not in_block:
            # Remove -- comment remainder
            stripped = line.split("--")[0]
            active_lines.append(stripped)
        if "*/" in line:
            in_block = False
    active_sql = "\n".join(active_lines)
    assert "incubator_temp_c" not in active_sql, \
        "Active SQL must not reference incubator_temp_c"


def test_bin_inserts_no_incubator_temp_c():
    """Bin INSERT statements in vault_admin_restore must not include incubator_temp_c."""
    sql = _load_migration_sql()
    # Find all INSERT INTO public.bin ... blocks
    bin_inserts = re.findall(
        r"INSERT INTO public\.bin\([^)]+\)",
        sql,
        re.IGNORECASE
    )
    for insert_line in bin_inserts:
        assert "incubator_temp_c" not in insert_line, \
            f"bin INSERT must not include incubator_temp_c: {insert_line[:80]}..."
