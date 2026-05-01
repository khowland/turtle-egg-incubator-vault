# CR-20260430-194500: Test database schema migration was applied correctly
"""
Verify post-migration column state:
- bin_observation: only incubator_temp_f (no ambient_temp or incubator_temp_c)
- bin: no incubator_temp_c
- system_log: observer_id exists
"""
import pytest


@pytest.mark.skipif("True", reason="Requires live Supabase connection")
def test_bin_observation_temp_column_renamed():
    """bin_observation must have incubator_temp_f, not ambient_temp or incubator_temp_c."""
    try:
        from utils.db import get_supabase_client
        supabase = get_supabase_client()
    except Exception as e:
        pytest.skip(f"Supabase unavailable: {e}")

    # Query information_schema for bin_observation columns
    result = supabase.rpc(
        "execute_sql",
        {"query": (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'bin_observation' AND table_schema = 'public' "
            "ORDER BY column_name"
        )}
    ).execute()

    col_names = {row["column_name"] for row in result.data} if result.data else set()

    if not col_names:
        pytest.skip("Could not query bin_observation columns")

    assert "incubator_temp_f" in col_names, "incubator_temp_f must exist"
    assert "ambient_temp" not in col_names, "ambient_temp must be gone"
    assert "incubator_temp_c" not in col_names, "incubator_temp_c must be gone"


@pytest.mark.skipif("True", reason="Requires live Supabase connection")
def test_bin_no_temp_column():
    """bin table must not have incubator_temp_c."""
    try:
        from utils.db import get_supabase_client
        supabase = get_supabase_client()
    except Exception as e:
        pytest.skip(f"Supabase unavailable: {e}")

    result = supabase.rpc(
        "execute_sql",
        {"query": (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'bin' AND table_schema = 'public' "
            "ORDER BY column_name"
        )}
    ).execute()

    col_names = {row["column_name"] for row in result.data} if result.data else set()
    assert "incubator_temp_c" not in col_names, "bin must not have incubator_temp_c"


@pytest.mark.skipif("True", reason="Requires live Supabase connection")
def test_system_log_has_observer_id():
    """system_log must have observer_id column."""
    try:
        from utils.db import get_supabase_client
        supabase = get_supabase_client()
    except Exception as e:
        pytest.skip(f"Supabase unavailable: {e}")

    result = supabase.rpc(
        "execute_sql",
        {"query": (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'system_log' AND table_schema = 'public' "
            "ORDER BY column_name"
        )}
    ).execute()

    col_names = {row["column_name"] for row in result.data} if result.data else set()
    assert "observer_id" in col_names, "system_log must have observer_id"
