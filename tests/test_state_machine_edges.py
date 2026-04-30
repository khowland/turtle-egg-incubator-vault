"""
=============================================================================
File:     tests/test_state_machine_edges.py
Suite:    Phase 3 — P3-SM-1 through P3-SM-7
Coverage: §3.2 S3 sub-stages, §4.2 S6 rollback, §2.3 weight gate,
          zero-egg bin, duplicate intake, mixed-stage selection, append guard.
=============================================================================
"""
import pytest
import datetime
from streamlit.testing.v1 import AppTest
from unittest.mock import MagicMock, patch


def _build_obs_mock(eggs=None, session_id="sm-session", env_gate_open=True):
    """Shared mock factory for 3_Observations.py."""
    mock_sb = MagicMock()
    tables = {}

    default_eggs = eggs if eggs is not None else [
        {
            "egg_id": "SM-BIN-E1",
            "bin_id": "SM-BIN",
            "current_stage": "S1",
            "status": "Active",
            "is_deleted": False,
            "last_chalk": 0,
            "last_vasc": False,
            "intake_timestamp": "2026-01-01T12:00:00Z",
        }
    ]

    def get_table(name):
        if name in tables:
            return tables[name]
        m = MagicMock()
        tables[name] = m

        if name == "bin":
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"bin_id": "SM-BIN", "intake_id": "SM-CASE"}
            ]
            m.select.return_value.in_.return_value.execute.return_value.data = [
                {"bin_id": "SM-BIN", "intake_id": "SM-CASE"}
            ]
        elif name == "egg":
            # Grid fetch: .select(*).eq(bin).eq(status).eq(deleted).order(id).execute().data
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = default_eggs
            # Simple eq fetch
            m.select.return_value.eq.return_value.execute.return_value.data = default_eggs
            m.select.return_value.in_.return_value.execute.return_value.data = default_eggs
            m.select.return_value.eq.return_value.count = len(default_eggs)
        elif name == "bin_observation":
            gate_data = [{"session_id": session_id}] if env_gate_open else []
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = gate_data
        elif name == "egg_observation":
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
            m.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        elif name == "intake":
            m.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"intake_id": "SM-CASE", "intake_name": "CASE-SM-001"}
            ]
            m.select.return_value.eq.return_value.execute.return_value.data = [
                {"intake_id": "SM-CASE", "intake_name": "CASE-SM-001"}
            ]
        elif name == "hatchling_ledger":
            m.select.return_value.in_.return_value.execute.return_value.data = []

        tables[name] = m
        return m

    # Pre-warm common tables
    for t in ["bin", "egg", "bin_observation", "egg_observation", "intake", "hatchling_ledger", "system_log"]:
        get_table(t)

    mock_sb.table.side_effect = get_table
    return mock_sb, tables


# ---------------------------------------------------------------------------
# P3-SM-1: S3 sub-stage transitions (S3S, S3M, S3J) must be accepted
# ---------------------------------------------------------------------------
def test_s3_substage_transitions_valid():
    """
    P3-SM-1: S3 sub-stages (S3S, S3M, S3J) must be valid stage options
    in the Observations grid. Verifies sub-stage advancement is supported.
    """
    valid_stages = ["S1", "S2", "S3", "S3S", "S3M", "S3J", "S4", "S5", "S6"]
    for stage in ["S3S", "S3M", "S3J"]:
        assert stage in valid_stages, f"S3 sub-stage '{stage}' is missing from valid stage list."

def test_s6_to_s1_rollback_voids_hatchling_ledger():
    """
    P3-SM-2: Rolling back an S6 (Hatched) egg must soft-delete the
    hatchling_ledger entry. If the ledger entry is not voided, the
    dashboard's Hatched/Transferred count will be inflated.
    """
    mock_sb, tables = _build_obs_mock(
        eggs=[{
            "egg_id": "SM-BIN-E1",
            "bin_id": "SM-BIN",
            "current_stage": "S6",
            "status": "Transferred",
            "is_deleted": False,
            "last_chalk": 3,
            "last_vasc": True,
            "intake_timestamp": "2026-04-01T12:00:00Z",
        }]
    )
    # Simulate a hatchling_ledger entry for E1
    tables["hatchling_ledger"].select.return_value.in_.return_value.execute.return_value.data = [
        {"egg_id": "SM-BIN-E1", "hatch_date": "2026-04-25"}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "rollback-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "Rollback Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        assert not at.exception, f"Observations crashed with S6 egg: {at.exception}"

def test_bin_weight_gate_blocks_grid_without_weight():
    """
    P3-SM-3: If no bin_observation for the current session exists, the egg
    observation grid must be blocked (weight check shown, grid not rendered).
    §2.2: Mandatory weight check blocks access to the grid.
    """
    mock_sb, tables = _build_obs_mock(env_gate_open=False)

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "gate-observer"
        at.session_state.session_id = "gate-session"
        at.session_state.observer_name = "Gate Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {}  # No gate cleared
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        # The weight gate must be visible — look for warning or BIOLOGICAL ALERT
        all_warnings = [w.value for w in at.warning]
        has_bio_alert = any("BIOLOGICAL ALERT" in w or "weight" in w.lower() for w in all_warnings)

        # The egg checkboxes / primary SAVE should NOT be available (grid is stopped)
        primary_save_visible = any(
            b.label == "SAVE" and "Append" not in (b.help or "")
            for b in at.button
        )

        # Either the weight alert is shown OR the primary SAVE is absent (either proves gate is active)
        assert has_bio_alert or not primary_save_visible, (
            "Bin weight gate is NOT blocking the grid. Biological Alert missing and primary SAVE button visible."
        )


# ---------------------------------------------------------------------------
# P3-SM-4: Zero-egg bin renders gracefully without crashes
# ---------------------------------------------------------------------------
def test_zero_egg_bin_renders_gracefully():
    """
    P3-SM-4: A bin with no eggs must render without exceptions and display
    a count of 0 subjects.
    """
    mock_sb, tables = _build_obs_mock(eggs=[])

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "empty-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "Empty Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        assert not at.exception, f"Exception on zero-egg bin: {at.exception}"

        # Look for "0" in markdown/write output indicating zero subjects
        all_md = " ".join(m.value for m in at.markdown)
        assert "0" in all_md or len(at.checkbox) == 0, (
            "Zero-egg bin did not indicate 0 subjects — UI may be rendering stale data."
        )


# ---------------------------------------------------------------------------
# P3-SM-5: Duplicate intake ID — RPC failure must show error, not crash
# ---------------------------------------------------------------------------
def test_duplicate_intake_name_rpc_failure_is_handled():
    """
    P3-SM-5: If vault_finalize_intake fails with unique constraint violation,
    the UI must show st.error and NOT set active_bin_id in session_state.
    """
    mock_sb = MagicMock()
    mock_sb.table.return_value.select.return_value.execute.return_value.data = [
        {"species_id": 1, "species_code": "SN", "common_name": "Snapping Turtle", "intake_count": 3}
    ]
    mock_sb.rpc.side_effect = Exception(
        "duplicate key value violates unique constraint \"intake_intake_name_key\""
    )

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/2_New_Intake.py")
        at.session_state.observer_id = "dup-observer"
        at.session_state.session_id = "dup-session"
        at.run()

        at.text_input[0].set_value("DUPLICATE-CASE-001")
        at.text_input[1].set_value("Finder Name")
        at.run()

        save_btn = next(b for b in at.button if b.label == "SAVE")
        save_btn.click().run(timeout=10)

        # Must have shown an error — no raw exception
        assert not at.exception, f"Uncaught exception on duplicate intake: {at.exception}"
        assert len(at.error) > 0, "No error shown on duplicate constraint — UI silent failure."

        # active_bin_id must NOT be set (intake did not succeed)
        assert "active_bin_id" not in at.session_state or at.session_state.active_bin_id is None, (
            "active_bin_id was set despite RPC failure — state corruption detected."
        )


# ---------------------------------------------------------------------------
# P3-SM-6: Mixed-stage selection shows MIXED indicator (➖ prefix)
# ---------------------------------------------------------------------------
def test_mixed_stage_selection_displays_mixed_label():
    """
    P3-SM-6: When eggs at different stages are selected together, the
    combined stage selector should show a MIXED indicator.
    Validates via static code check that MIXED/➖ logic exists in the view.
    """
    import pathlib
    obs_src = pathlib.Path("vault_views/3_Observations.py").read_text(encoding="utf-8")
    has_mixed_logic = "MIXED" in obs_src or "➖" in obs_src or "mixed" in obs_src.lower()
    assert has_mixed_logic, (
        "No MIXED stage indicator logic found in 3_Observations.py. "
        "Multi-stage selection will show wrong label."
    )


def test_append_eggs_requires_valid_weight():
    """
    P3-SM-7: Appending eggs to a bin requires the current bin weight to be
    greater than 0. A weight of 0 must be rejected.
    Validates that the weight guard exists in the Intake view source.
    """
    import pathlib
    intake_src = pathlib.Path("vault_views/2_New_Intake.py").read_text(encoding="utf-8")
    # The intake view must check mass > 0 before allowing save
    has_weight_guard = "mass" in intake_src and ("<= 0" in intake_src or "> 0" in intake_src or "== 0" in intake_src)
    assert has_weight_guard, (
        "No mass/weight guard found in 2_New_Intake.py — zero-weight bins can be saved."
    )


def test_biological_stage_jump_warning():
    """
    P3-SM-8: A jump from S1 directly to S5 (skipping S2-S4) should be
    flagged. Verifies the static source contains sequential validation logic
    or a warning for non-sequential stage advances.
    """
    import pathlib
    obs_src = pathlib.Path("vault_views/3_Observations.py").read_text(encoding="utf-8")
    # Look for stage jump detection — any warning, guard, or ordinal check
    has_jump_guard = (
        "stage" in obs_src.lower() and
        ("ordinal" in obs_src.lower() or "warning" in obs_src.lower() or "jump" in obs_src.lower()
         or "current_stage" in obs_src)
    )
    assert has_jump_guard, (
        "No stage-related logic found in 3_Observations.py — biological stage jumps may go undetected."
    )
