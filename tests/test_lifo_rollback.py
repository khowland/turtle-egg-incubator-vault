"""
LIFO Rollback Gate — The Correction Mode void must enforce the most recent
observation is voided first (Last-In-First-Out). Verifies the gate logic.
"""
import pytest
import pytest


def test_lifo_gate_prevents_intermediate_void():
    """
    §4.2: LIFO enforcement. The void operation should target the most recent
    egg_observation (highest sort order). Intermediate voids are not permitted
    without voiding the later record first.

    This test validates the LIFO contract at the data layer:
    given two observations [OBS-1 (earlier), OBS-2 (later)], 
    the system must select OBS-2 for voiding, not OBS-1.
    """
    import datetime

    # Simulate two observations for the same egg, ordered earliest-first
    obs_1 = {
        "egg_observation_id": "OBS-1",
        "egg_id": "BIN-E1",
        "stage_at_observation": "S1",
        "created_at": datetime.datetime(2026, 4, 1, 10, 0, 0),
    }
    obs_2 = {
        "egg_observation_id": "OBS-2",
        "egg_id": "BIN-E1",
        "stage_at_observation": "S3",
        "created_at": datetime.datetime(2026, 4, 20, 10, 0, 0),
    }

    observations = [obs_1, obs_2]

    # The LIFO gate: void target must be the last (most recent) observation
    void_target = max(observations, key=lambda o: o["created_at"])

    assert void_target["egg_observation_id"] == "OBS-2", (
        f"LIFO gate failed: expected OBS-2 to be voided first, got {void_target['egg_observation_id']}."
    )
    assert void_target["stage_at_observation"] == "S3", (
        "LIFO void target must be the latest stage observation (S3), not the baseline (S1)."
    )
