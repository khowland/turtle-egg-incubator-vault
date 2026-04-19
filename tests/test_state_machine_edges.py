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
    P3-SM-1: Stage S3S, S3M, S3J must be accepted in egg_observation payload.
    §3.2: Individual biological subjects have developmental stages S0-S6.
    """
    mock_sb, tables = _build_obs_mock()

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "sm-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "SM Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        egg_cb = next((cb for cb in at.checkbox if "1" in cb.label), None)
        assert egg_cb is not None, f"Egg checkbox not found. Available: {[cb.label for cb in at.checkbox]}"
        egg_cb.check().run(timeout=15)

        stage_sel = next((s for s in at.selectbox if "Stage" in (s.label or "")), None)
        assert stage_sel is not None, "Stage selectbox not found."
        assert "S3S" in stage_sel.options, "S3S is not in stage options — sub-stage support missing."

        stage_sel.set_value("S3S").run(timeout=15)

        save_btn = next((b for b in at.button if b.label == "SAVE" and "Append" not in (b.help or "")), None)
        assert save_btn is not None, "Primary SAVE button not found."
        save_btn.click().run(timeout=15)

        insert_calls = tables["egg_observation"].insert.call_args_list
        assert len(insert_calls) > 0, "egg_observation.insert not called."
        payload = insert_calls[-1][0][0]
        if isinstance(payload, list):
            payload = payload[0]
        assert payload.get("stage_at_observation") == "S3S", (
            f"S3S sub-stage not recorded. Got: {payload.get('stage_at_observation')}"
        )


# ---------------------------------------------------------------------------
# P3-SM-2: S6 void rollback must also void hatchling_ledger
# ---------------------------------------------------------------------------
def test_s6_to_s1_rollback_voids_hatchling_ledger():
    """
    P3-SM-2: When a S6 (Hatched) observation is voided in Correction Mode,
    hatchling_ledger entries for that egg must be soft-deleted.
    §4.2: Correction Mode handles hatchling ledger rollbacks.
    """
    mock_sb, tables = _build_obs_mock()

    # Prime an S6 egg history
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = [
        {
            "egg_observation_id": "OBS-S6-001",
            "egg_id": "SM-BIN-E1",
            "timestamp": "2026-02-01T10:00:00Z",
            "stage_at_observation": "S6",
            "observer_id": "sm-observer",
            "chalking": 0, "vascularity": True, "molding": 0, "leaking": 0,
            "is_deleted": False,
        }
    ]
    # After void, remaining observations show S5
    tables["egg_observation"].select.return_value.eq.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"stage_at_observation": "S5"}
    ]
    # Hatchling ledger has an entry
    tables["hatchling_ledger"].select.return_value.in_.return_value.execute.return_value.data = [
        {"hatchling_ledger_id": "HL-001", "egg_id": "SM-BIN-E1"}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("utils.bootstrap.get_resilient_table", side_effect=lambda sb, name: mock_sb.table(name)), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "sm-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "SM Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        surg_toggle = next((t for t in at.toggle if "Correction" in t.label or "Surgical" in t.label), None)
        assert surg_toggle is not None, "Correction Mode toggle not found."
        surg_toggle.set_value(True).run(timeout=15)

        void_btn = next((b for b in at.button if b.label == "REMOVE"), None)
        assert void_btn is not None, "REMOVE button not found."
        void_btn.click().run(timeout=15)

        # Assert hatchling_ledger.update called with is_deleted=True
        hl_updates = tables["hatchling_ledger"].update.call_args_list
        assert len(hl_updates) > 0, (
            "S6 rollback did NOT call hatchling_ledger.update — ledger entries not voided."
        )
        hl_payload = hl_updates[-1][0][0]
        assert hl_payload.get("is_deleted") is True, (
            f"hatchling_ledger.update did not set is_deleted=True. Got: {hl_payload}"
        )

        # No hard delete allowed
        delete_calls = tables["hatchling_ledger"].delete.call_args_list
        assert len(delete_calls) == 0, "Hard DELETE was called on hatchling_ledger — soft-delete violation!"


# ---------------------------------------------------------------------------
# P3-SM-3: Bin weight gate blocks the grid when no weight on record
# ---------------------------------------------------------------------------
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
    P3-SM-6: When eggs at different stages are both selected, the stage
    selectbox label must include the '➖' mixed indicator.
    """
    mixed_eggs = [
        {
            "egg_id": "SM-BIN-E1", "bin_id": "SM-BIN", "current_stage": "S1",
            "status": "Active", "is_deleted": False, "last_chalk": 0,
            "last_vasc": False, "intake_timestamp": "2026-01-01T12:00:00Z",
        },
        {
            "egg_id": "SM-BIN-E2", "bin_id": "SM-BIN", "current_stage": "S2",
            "status": "Active", "is_deleted": False, "last_chalk": 0,
            "last_vasc": False, "intake_timestamp": "2026-01-05T12:00:00Z",
        },
    ]
    mock_sb, tables = _build_obs_mock(eggs=mixed_eggs)

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "mixed-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "Mixed Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        # Select first egg (S1)
        cb1 = next((cb for cb in at.checkbox if "1" in cb.label), None)
        cb2 = next((cb for cb in at.checkbox if "2" in cb.label), None)
        assert cb1 is not None and cb2 is not None, (
            f"Could not find both egg checkboxes. Found: {[cb.label for cb in at.checkbox]}"
        )
        cb1.check().run(timeout=15)
        cb2.check().run(timeout=15)

        # The stage selectbox label should indicate mixed state
        stage_sel = next((s for s in at.selectbox if "Stage" in (s.label or "")), None)
        assert stage_sel is not None, "Stage selectbox not found after selecting 2 eggs."
        assert "➖" in (stage_sel.label or ""), (
            f"Mixed-stage indicator '➖' not found in label. Got: '{stage_sel.label}'"
        )


# ---------------------------------------------------------------------------
# P3-SM-7: Append eggs requires valid (> 0) weight input
# ---------------------------------------------------------------------------
def test_append_eggs_requires_valid_weight():
    """
    P3-SM-7: In the 'Add Eggs to Existing Bin' sidebar expander, if
    New Post-Append Mass is 0, the INSERT must be blocked with an error.
    """
    mock_sb, tables = _build_obs_mock()
    # Intake records for the supplemental bin sidebar
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        {"intake_id": "SM-CASE", "intake_name": "CASE-SM-001", "is_deleted": False}
    ]

    with patch("utils.bootstrap.bootstrap_page", return_value=mock_sb), \
         patch("streamlit.switch_page") as mock_switch:
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "append-observer"
        at.session_state.session_id = "sm-session"
        at.session_state.observer_name = "Append Tester"
        at.session_state.workbench_bins = {"SM-BIN"}
        at.session_state.env_gate_synced = {"SM-BIN": True}
        at.run(timeout=15)

        if at.exception:
            if isinstance(at.exception[0], BaseException):
                raise at.exception[0]
            else:
                pytest.fail(f"Script exception: {at.exception[0]}")

        # Set Eggs to Add = 3, leave Post-Append Mass = 0.0 (default)
        eggs_ni = next((n for n in at.number_input if "Eggs to Add" in (n.label or "")), None)
        if eggs_ni:
            eggs_ni.set_value(3)

        # Click the SAVE in the append expander (help text contains "Append")
        append_save = next(
            (b for b in at.button if b.label == "SAVE" and "Append" in (b.help or "")), None
        )
        if append_save is None:
            # Fallback: find SAVE that's not the primary observation SAVE
            append_save = next(
                (b for b in at.button if b.label == "SAVE" and getattr(b, "type", "") != "primary"), None
            )

        assert append_save is not None, "Append SAVE button not found in sidebar."
        append_save.click().run(timeout=15)

        # Must show an error about weight
        assert len(at.error) > 0, (
            "No validation error shown when Post-Append Mass is 0 — guard not enforced."
        )
        # egg.insert must NOT have been called
        insert_calls = tables["egg"].insert.call_args_list
        assert len(insert_calls) == 0, (
            "egg.insert was called despite invalid weight input — data integrity violation."
        )
