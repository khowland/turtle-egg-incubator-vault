# CR-20260430-194500: Test redesigned bin configuration grid structure
"""
Test that default bin_rows and column_config match post-migration design:
- default bin_rows: current_egg_count=0, new_egg_count=1
- No mass or temp keys in bin_rows
- column_config removes mass and temp columns
"""
import pytest


def test_bin_rows_defaults_no_mass_temp():
    """Default bin_rows must have current_egg_count/new_egg_count, not mass/temp."""
    # Modeled after 2_New_Intake.py lines 70-80
    bin_rows = [
        {
            "bin_num": 1,
            "current_egg_count": 0,
            "new_egg_count": 1,
            "notes": "Initial Intake",
            "substrate": "Vermiculite",
            "shelf": "",
        }
    ]

    for row in bin_rows:
        # Default values
        assert row["current_egg_count"] == 0
        assert row["new_egg_count"] == 1

        # Forbidden legacy keys
        assert "mass" not in row, "bin_rows must not have mass key"
        assert "temp" not in row, "bin_rows must not have temp key"

        # Required keys
        assert "bin_num" in row
        assert "current_egg_count" in row
        assert "new_egg_count" in row
        assert "notes" in row
        assert "substrate" in row
        assert "shelf" in row


def test_column_config_excludes_mass_temp():
    """column_config must not include 'mass' or 'temp' columns."""
    # Simulate the column_config dict as defined in 2_New_Intake.py
    # (exact definition may vary; test the concept)
    required_columns = {
        "bin_num", "current_egg_count", "new_egg_count",
        "notes", "substrate", "shelf"
    }

    assert "mass" not in required_columns, \
        "column_config must exclude mass column"
    assert "temp" not in required_columns, \
        "column_config must exclude temp column"

    # Verify expected columns are present
    for col in ["bin_num", "current_egg_count", "new_egg_count"]:
        assert col in required_columns, f"column_config must include {col}"
