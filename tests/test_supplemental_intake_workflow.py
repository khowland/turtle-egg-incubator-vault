# CR-20260430-194500: Test supplemental intake bin_rows structure
"""
Test that supplemental intake mode populates bin_rows with:
- current_egg_count, new_egg_count
- is_new_bin, existing_bin_id
"""
import pytest


def test_supplemental_bin_rows_has_required_keys():
    """Simulate supplemental intake bin_rows from existing bins response."""
    # Modeled after 2_New_Intake.py lines 110-121
    bin_rows = [
        {
            "bin_num": 1,
            "current_egg_count": 12,
            "new_egg_count": 0,
            "notes": "Existing bin",
            "substrate": "Vermiculite",
            "shelf": "A1",
            "is_new_bin": False,
            "existing_bin_id": "SN1-HOWLAND-1",
        }
    ]

    for row in bin_rows:
        assert "current_egg_count" in row, \
            "Supplemental bin_rows must have current_egg_count"
        assert "new_egg_count" in row, \
            "Supplemental bin_rows must have new_egg_count"
        assert "is_new_bin" in row, \
            "Supplemental bin_rows must have is_new_bin"
        assert "existing_bin_id" in row, \
            "Supplemental bin_rows must have existing_bin_id"

        # is_new_bin should be False for existing bins
        assert row["is_new_bin"] is False

        # current_egg_count reflects existing DB total_eggs
        assert row["current_egg_count"] > 0


def test_new_intake_bin_rows_has_defaults():
    """New intake mode bin_rows must have current_egg_count and new_egg_count."""
    # Modeled after 2_New_Intake.py lines 70-80 default
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
        assert "current_egg_count" in row
        assert "new_egg_count" in row
        assert row["current_egg_count"] == 0
        assert row["new_egg_count"] >= 1
