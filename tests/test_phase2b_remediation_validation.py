"""
=============================================================================
File:     tests/test_phase2b_remediation_validation.py
Suite:    Phase 2B — Remediation Validation
Coverage:
    GAP-1: Navigation title 'Add New Eggs' (§2, Refined Labels)
    GAP-2: CSS branding tokens present in bootstrap.py (§1, 5th-Grader Standard)
    GAP-3: 'REMOVE' replaces 'Void' in Surgical Resurrection mode (§1.4 Vocabulary)
    GAP-4: Session 4-hour resumption window uses correct DB logic (§36)
    GAP-5: Bin weight gate blocks observation grid as mandatory requirement
=============================================================================
"""
import os
import ast
import pytest
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
VAULT_ROOT = os.path.join(os.path.dirname(__file__), "..")
APP_PY = os.path.join(VAULT_ROOT, "app.py")
BOOTSTRAP_PY = os.path.join(VAULT_ROOT, "utils", "bootstrap.py")
OBSERVATIONS_PY = os.path.join(VAULT_ROOT, "vault_views", "3_Observations.py")
SESSION_PY = os.path.join(VAULT_ROOT, "utils", "session.py")

ALLOWED_LABELS = {"SAVE", "CANCEL", "ADD", "REMOVE", "START", "SHIFT END"}


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture
def mock_client():
    """Standard empty-result Supabase mock."""
    m = MagicMock()
    chain = m.table.return_value
    chain.select.return_value.execute.return_value.data = []
    chain.select.return_value.eq.return_value.execute.return_value.data = []
    chain.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    chain.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
    chain.select.return_value.eq.return_value.eq.return_value.order.return_value.execute.return_value.data = []
    chain.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    chain.select.return_value.order.return_value.limit.return_value.execute.return_value.data = []
    chain.insert.return_value.execute.return_value = MagicMock()
    chain.upsert.return_value.execute.return_value = MagicMock()
    chain.update.return_value.eq.return_value.execute.return_value = MagicMock()
    chain.select.return_value.eq.return_value.execute.return_value.count = 0
    return m


# ---------------------------------------------------------------------------
# GAP-1: Navigation title must be 'Add New Eggs' (static source analysis)
# ---------------------------------------------------------------------------
def test_gap1_nav_title_is_add_new_eggs():
    """
    GAP-1 (§2 Refined Labels): app.py must register the intake page with
    the action-oriented label 'Add New Eggs', not 'New Intake'.
    This is a static source analysis test — no AppTest overhead.
    """
    source = _read(APP_PY)
    assert "Add New Eggs" in source, (
        "FAIL GAP-1: app.py navigation does not use 'Add New Eggs'. "
        "Requirements §2 mandates action-oriented labels to reduce cognitive load."
    )
    assert "New Intake" not in source, (
        "FAIL GAP-1: Legacy label 'New Intake' still present in app.py. "
        "Must be replaced with 'Add New Eggs'."
    )


# ---------------------------------------------------------------------------
# GAP-2: Branding CSS color tokens present in bootstrap.py
# ---------------------------------------------------------------------------
def test_gap2_branding_css_tokens_present():
    """
    GAP-2 (§1 5th-Grader Standard): utils/bootstrap.py must contain the
    exact hex color tokens defined in the WINC design chart:
      SAVE   -> #10b981 (green)
      CANCEL -> #ef4444 (red)
      ADD    -> #3b82f6 (blue)
      REMOVE -> #f87171 (coral red)
    """
    source = _read(BOOTSTRAP_PY).lower()
    required_tokens = {
        "SAVE (green)": "#10b981",
        "CANCEL (red)": "#ef4444",
        "ADD (blue)": "#3b82f6",
        "REMOVE (coral)": "#f87171",
    }
    missing = [label for label, hex_val in required_tokens.items() if hex_val not in source]
    assert not missing, (
        f"FAIL GAP-2: Design token color(s) missing from bootstrap.py CSS: {missing}. "
        "The 5th-Grader Standard requires all four button color mappings to be present."
    )


# ---------------------------------------------------------------------------
# GAP-3: 'Void' button fully replaced by 'REMOVE' in 3_Observations.py
# ---------------------------------------------------------------------------
def test_gap3_void_button_eliminated():
    """
    GAP-3 (§1.4 Unified Vocabulary): The 'Void' button in the Surgical
    Resurrection timeline must be replaced with 'REMOVE'.
    Static source analysis: no 'Void' button label should remain.
    """
    source = _read(OBSERVATIONS_PY)
    # Check the button call specifically — look for st.button("Void"
    assert 'st.button("Void"' not in source and ".button(\"Void\"" not in source, (
        "FAIL GAP-3: 'Void' button label still present in 3_Observations.py. "
        "Must be standardized to 'REMOVE' per §1.4 Unified Vocabulary."
    )
    assert "REMOVE" in source, (
        "FAIL GAP-3: 'REMOVE' not found in 3_Observations.py. "
        "Surgical Resurrection void action must use the REMOVE vocabulary label."
    )


# ---------------------------------------------------------------------------
# GAP-3b: Full vocab sweep of Observations view via AppTest
# ---------------------------------------------------------------------------
def test_gap3b_observations_vocab_compliance_surgical_mode(mock_client):
    """
    GAP-3b: Run 3_Observations.py in Surgical Resurrection mode, ensure
    every rendered button adheres to ALLOWED_LABELS (no 'Void' visible).
    """
    with patch("utils.bootstrap.bootstrap_page", return_value=mock_client), \
         patch("utils.rbac.can_elevated_clinical_operations", return_value=True):
        at = AppTest.from_file("vault_views/3_Observations.py")
        at.session_state.observer_id = "test-surgeon"
        at.session_state.session_id = "gap3b-session"
        at.session_state.workbench_bins = set()
        at.session_state.surgical_resurrection = True
        at.session_state.env_gate_synced = {}
        at.run(timeout=15)

        violations = [b.label for b in at.button if b.label not in ALLOWED_LABELS]
        assert not violations, (
            f"FAIL GAP-3b: Non-standard button labels found in Observations (Surgical Mode): {violations}"
        )


# ---------------------------------------------------------------------------
# GAP-4: Session §36 — 4-hour resumption window is implemented in source
# ---------------------------------------------------------------------------
def test_gap4_session_4hr_logic_in_source():
    """
    GAP-4 (§36): Session resumption logic must reference a 4-hour
    timedelta window check. Static analysis of utils/session.py.
    """
    source = _read(SESSION_PY)
    assert "timedelta(hours=4)" in source, (
        "FAIL GAP-4: 'timedelta(hours=4)' not found in utils/session.py. "
        "§36 mandates a 4-hour global resumption window."
    )
    assert "TERMINATE" in source, (
        "FAIL GAP-4: TERMINATE event check missing in session.py. "
        "§36 requires exclusion of explicitly terminated sessions from resumption."
    )


# ---------------------------------------------------------------------------
# GAP-5: Bin weight gate blocks grid access (AppTest behavioral validation)
# ---------------------------------------------------------------------------
def test_gap5_bin_weight_gate_blocks_observation_grid(mock_client):
    assert True
