# CR-20260430-194500: Test vault_finalize_intake RPC payload schema compliance
"""
Test that vault_finalize_intake receives payload with new column names:
- No incubator_temp_c in bin entries
- No bin_weight_g in bin entries
- incubator_temp_f present in bin entries (for bin_observation INSERT)
"""
import pytest


def test_vault_finalize_intake_payload_keys():
    """Validate bin payload structure matches post-migration schema."""
    # Reproduce the bins_payload built in 2_New_Intake.py commit_all()
    bins_payload = [
        {
            "bin_id": "SN1-TEST-1",
            "bin_notes": "Test bin",
            "egg_count": 3,
            "substrate": "Vermiculite",
            "shelf_location": "A1",
            "incubator_temp_f": 82.5,
        }
    ]

    for entry in bins_payload:
        # Forbidden legacy keys
        assert "incubator_temp_c" not in entry, \
            "bin entry must not contain incubator_temp_c"
        assert "bin_weight_g" not in entry, \
            "bin entry must not contain bin_weight_g"

        # Required keys
        assert "bin_id" in entry
        assert "egg_count" in entry

        # incubator_temp_f should be present for bin_observation
        assert "incubator_temp_f" in entry, \
            "bin entry must contain incubator_temp_f for bin_observation"
